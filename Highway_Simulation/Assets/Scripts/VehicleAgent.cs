using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class VehicleAgent : MonoBehaviour
{
    public enum VehicleState { Normal, WrongLane, Crashed }

    [Header("Path")]
    public List<Transform> waypoints = new List<Transform>();

    [Header("Motion")]
    public float maxSpeed  = 4f;
    public float accel     = 6f;
    public float turnSpeed = 8f;
    public float waypointReachDistance = 0.3f;

    [Header("Traffic Awareness")]
    public float slowDownDistance = 5f;
    public float safeGap          = 0.8f;
    public LayerMask vehicleLayer;

    [Header("Accident Detection")]
    [Tooltip("Minimum speed both vehicles must exceed to trigger accident")]
    public float minCrashSpeed = 0.35f;

    [Header("Deadlock Prevention")]
    [Tooltip("Seconds stopped before deadlock override kicks in")]
    public float deadlockLimit = 3f;

    [Header("Debug")]
    public bool debugLogs = true;

    public VehicleState state = VehicleState.Normal;
    [HideInInspector] public float currentSpeed = 0f;

    private int   currentIndex  = 0;
    private bool  _fadingOut    = false;
    private float _overlapTimer = 0f;
    private bool  _isWrongLane  = false;
    private float _stoppedTimer = 0f;

    private TrafficSignal _waitingAtSignal = null;
    private JunctionYield _pendingJunction = null;

    private static HashSet<VehicleAgent> _activeCrashes =
        new HashSet<VehicleAgent>();

    void Update()
    {
        if (state == VehicleState.Crashed) return;
        if (_fadingOut) return;
        if (waypoints == null || waypoints.Count == 0) return;
        if (currentIndex >= waypoints.Count)
        {
            StartCoroutine(FadeAndDestroy());
            return;
        }
        MoveVehicle();
        CheckOverlapAccident();
    }

    void MoveVehicle()
    {
        Transform target = waypoints[currentIndex];
        if (target == null) { currentIndex++; return; }

        // ── SIGNAL CHECK ──────────────────────────────────────────────────
        if (_waitingAtSignal != null)
        {
            if (!_waitingAtSignal.isGreen)
            {
                currentSpeed = 0f;
                return;
            }
            else
            {
                _waitingAtSignal = null;
            }
        }

        // ── JUNCTION YIELD CHECK ──────────────────────────────────────────
        if (_pendingJunction != null)
        {
            if (!_pendingJunction.IsJunctionClear(gameObject))
            {
                currentSpeed = 0f;
                return;
            }
            else
            {
                _pendingJunction = null;
            }
        }

        Vector2 dir = (target.position - transform.position);

        if (dir.sqrMagnitude > 0.001f)
        {
            float targetAngle  = Mathf.Atan2(dir.y, dir.x) * Mathf.Rad2Deg;
            float adaptiveTurn = turnSpeed * (1f + currentSpeed /
                                 Mathf.Max(maxSpeed, 0.1f));
            float angle = Mathf.LerpAngle(transform.eulerAngles.z, targetAngle,
                                           adaptiveTurn * Time.deltaTime);
            transform.rotation = Quaternion.Euler(0, 0, angle);
        }

        float targetSpeed = ScanAhead();
        float useAccel    = targetSpeed < currentSpeed ? accel * 10f : accel;
        currentSpeed = Mathf.MoveTowards(currentSpeed, targetSpeed,
                                          useAccel * Time.deltaTime);

        transform.position += transform.right * currentSpeed * Time.deltaTime;

        if (Vector2.Distance(transform.position, target.position)
            <= waypointReachDistance)
        {
            bool branched = TryBranchAt(target);
            currentIndex++;
            if (currentIndex >= waypoints.Count)
            {
                if (branched)
                    currentIndex = Mathf.Clamp(currentIndex,
                                               0, waypoints.Count - 1);
                else
                    StartCoroutine(FadeAndDestroy());
            }
        }
    }

    public void SetSignalRed(TrafficSignal signal)
    {
        if (state == VehicleState.Crashed) return;
        _waitingAtSignal = signal;
    }

    public void SetSignalGreen()
    {
        _waitingAtSignal = null;
    }

    public void ApproachingJunction(JunctionYield junction)
    {
        if (state == VehicleState.Crashed) return;
        if (!junction.IsJunctionClear(gameObject))
            _pendingJunction = junction;
    }

    float ScanAhead()
    {
        Vector2 castDir = transform.right;
        if (currentIndex < waypoints.Count && waypoints[currentIndex] != null)
        {
            Vector2 toWaypoint = (Vector2)waypoints[currentIndex].position
                                 - (Vector2)transform.position;
            if (toWaypoint.sqrMagnitude > 0.01f)
                castDir = toWaypoint.normalized;
        }

        float castRadius = 0.55f;

        // Only run deadlock breaker if not held by signal or junction
        if (currentSpeed <= 0.05f &&
            _waitingAtSignal == null &&
            _pendingJunction == null)
        {
            _stoppedTimer += Time.deltaTime;
            if (_stoppedTimer >= deadlockLimit)
            {
                bool legitimateStop = false;
                foreach (VehicleAgent crash in _activeCrashes)
                {
                    if (crash == null) continue;
                    Vector2 toCrash = (Vector2)crash.transform.position -
                                      (Vector2)transform.position;
                    float dot = Vector2.Dot(castDir, toCrash.normalized);
                    if (dot < 0.5f) continue;
                    legitimateStop = true;
                    break;
                }
                if (!legitimateStop)
                {
                    _stoppedTimer = 0f;
                    return maxSpeed * 0.5f;
                }
            }
        }
        else
        {
            _stoppedTimer = 0f;
        }

        Vector2 immediateCenter = (Vector2)transform.position +
                                  castDir * (safeGap * 0.7f);

        Collider2D[] immediateHits = Physics2D.OverlapCircleAll(
            immediateCenter, castRadius * 0.7f, vehicleLayer);

        foreach (Collider2D c in immediateHits)
        {
            if (c.gameObject == gameObject) continue;
            VehicleAgent a = c.GetComponent<VehicleAgent>();
            if (a == null) continue;
            Vector2 toOther = ((Vector2)c.transform.position -
                               (Vector2)transform.position).normalized;
            float dot = Vector2.Dot(castDir, toOther);
            if (dot < 0.6f) continue;
            if (a.state == VehicleState.Crashed) return 0f;
            if (a.currentSpeed <= 0.05f) return 0f;
        }

        RaycastHit2D hit = Physics2D.CircleCast(
            (Vector2)transform.position + castDir * 0.3f,
            castRadius,
            castDir,
            slowDownDistance,
            vehicleLayer
        );

        if (hit.collider == null || hit.collider.gameObject == gameObject)
            return maxSpeed;

        VehicleAgent front = hit.collider.GetComponent<VehicleAgent>();
        float d = hit.distance;

        if (front != null)
        {
            Vector2 toFront = ((Vector2)hit.collider.transform.position -
                               (Vector2)transform.position).normalized;
            if (Vector2.Dot(castDir, toFront) < 0.6f) return maxSpeed;
        }

        if (front != null && front.state == VehicleState.Crashed)
        {
            if (d <= safeGap) return 0f;
            float t = (d - safeGap) / (slowDownDistance - safeGap);
            return Mathf.Lerp(0f, maxSpeed, Mathf.Clamp01(t));
        }

        if (d <= safeGap * 0.35f) return 0f;

        if (d <= safeGap)
        {
            float fSpd = front != null ? front.currentSpeed : 0f;
            if (fSpd <= 0.05f) return 0f;
            return Mathf.Min(fSpd, maxSpeed);
        }

        float ratio = (d - safeGap) / (slowDownDistance - safeGap);
        float spd   = Mathf.Lerp(0f, maxSpeed, ratio);
        if (front != null && front.currentSpeed < maxSpeed)
            spd = Mathf.Min(spd, front.currentSpeed + 0.5f);

        return spd;
    }

    void CheckOverlapAccident()
    {
        _overlapTimer += Time.deltaTime;
        if (_overlapTimer < 0.1f) return;
        _overlapTimer = 0f;

        Collider2D[] hits = Physics2D.OverlapCircleAll(
            transform.position, 0.4f, vehicleLayer);

        foreach (Collider2D hit in hits)
        {
            if (hit.gameObject == gameObject) continue;
            VehicleAgent other = hit.GetComponent<VehicleAgent>();
            if (other == null) continue;
            if (other.state == VehicleState.Crashed) continue;

            bool bothMoving = currentSpeed       > minCrashSpeed &&
                              other.currentSpeed > minCrashSpeed;
            if (!bothMoving) continue;

            bool headOn      = Vector2.Dot(transform.right,
                                            other.transform.right) < -0.5f;
            bool wrongLaneHit = _isWrongLane || other._isWrongLane;

            if (headOn || wrongLaneHit)
            {
                if (debugLogs) Debug.Log($"[Accident] {name} x {other.name}");
                other.SetCrashed();
                SetCrashed();
                return;
            }
        }
    }

    bool TryBranchAt(Transform wp)
    {
        var branch = wp.GetComponent<WaypointBranchParent>();
        if (branch == null)
        {
            if (debugLogs && currentIndex == waypoints.Count - 1)
                Debug.LogWarning($"[Vehicle] Last waypoint '{wp.name}' " +
                                  "has NO WaypointBranchParent.");
            return false;
        }

        List<Transform> newRoute = branch.PickRoute();
        if (newRoute == null || newRoute.Count == 0) return false;

        List<Transform> updated = new List<Transform>();
        for (int i = 0; i <= currentIndex && i < waypoints.Count; i++)
            updated.Add(waypoints[i]);
        if (newRoute.Count > 0 && newRoute[0] == wp) newRoute.RemoveAt(0);
        updated.AddRange(newRoute);
        waypoints = updated;

        if (debugLogs)
            Debug.Log($"[Vehicle] Branch appended. Total = {waypoints.Count}");
        return true;
    }

    public void SetCrashed()
    {
        if (state == VehicleState.Crashed) return;
        state            = VehicleState.Crashed;
        currentSpeed     = 0f;
        _waitingAtSignal = null;
        _pendingJunction = null;

        _activeCrashes.Add(this);

        Rigidbody2D rb = GetComponent<Rigidbody2D>();
        if (rb != null)
        {
            rb.linearVelocity  = Vector2.zero;
            rb.angularVelocity = 0f;
            rb.constraints     = RigidbodyConstraints2D.FreezeAll;
        }

        Collider2D col = GetComponent<Collider2D>();
        if (col != null) col.isTrigger = true;

        SpriteRenderer sr = GetComponentInChildren<SpriteRenderer>();
        if (sr != null) { sr.enabled = true; sr.color = Color.red; }

        if (debugLogs) Debug.Log($"[Vehicle] {name} CRASHED.");
        StartCoroutine(CrashVisibility(6f));
    }

    private IEnumerator CrashVisibility(float duration)
    {
        SpriteRenderer sr = GetComponentInChildren<SpriteRenderer>();
        if (sr != null) { sr.enabled = true; sr.color = Color.red; }

        yield return new WaitForSeconds(duration);

        float t = 1f;
        while (t > 0f)
        {
            t -= Time.deltaTime * 1.5f;
            if (sr != null)
                sr.color = new Color(1f, 0f, 0f, Mathf.Max(t, 0f));
            yield return null;
        }

        _activeCrashes.Remove(this);
        StartCoroutine(ReleaseQueue());

        Collider2D col = GetComponent<Collider2D>();
        if (col != null) col.isTrigger = false;

        Rigidbody2D rb = GetComponent<Rigidbody2D>();
        if (rb != null) rb.constraints = RigidbodyConstraints2D.None;

        Destroy(gameObject);
    }

    private IEnumerator ReleaseQueue()
    {
        Vector3 crashPos = transform.position;

        VehicleAgent[] allVehicles = FindObjectsByType<VehicleAgent>(
            FindObjectsSortMode.None);

        System.Array.Sort(allVehicles, (a, b) =>
        {
            float distA = Vector3.Distance(a.transform.position, crashPos);
            float distB = Vector3.Distance(b.transform.position, crashPos);
            return distA.CompareTo(distB);
        });

        foreach (VehicleAgent v in allVehicles)
        {
            if (v == null) continue;
            if (v.state == VehicleState.Crashed) continue;
            if (v.currentSpeed > 0.05f) continue;
            if (v._waitingAtSignal != null) continue;

            v.currentSpeed = v.maxSpeed * 0.3f;
            yield return new WaitForSeconds(0.25f + Random.Range(0f, 0.15f));
        }
    }

    IEnumerator FadeAndDestroy()
    {
        if (_fadingOut) yield break;
        _fadingOut = true;
        state      = VehicleState.Crashed;

        SpriteRenderer sr = GetComponentInChildren<SpriteRenderer>();
        float t = 1f;
        while (t > 0f)
        {
            t -= Time.deltaTime * 2f;
            if (sr != null)
                sr.color = new Color(sr.color.r, sr.color.g, sr.color.b,
                                     Mathf.Max(t, 0f));
            yield return null;
        }
        Destroy(gameObject);
    }

    void SetupWrongLane(List<Transform> original)
    {
        _isWrongLane = true;
        state        = VehicleState.WrongLane;
        waypoints    = new List<Transform>(original);
        waypoints.Reverse();
        currentIndex = 0;
    }

    public void SnapFacingToNextWaypoint()
    {
        if (waypoints == null || waypoints.Count == 0) return;
        int idx = 0;
        if (Vector2.Distance(transform.position, waypoints[0].position) < 0.2f
            && waypoints.Count > 1) idx = 1;
        Vector2 dir = waypoints[idx].position - transform.position;
        if (dir.sqrMagnitude < 0.001f) return;
        transform.rotation = Quaternion.Euler(0, 0,
            Mathf.Atan2(dir.y, dir.x) * Mathf.Rad2Deg);
    }

    public void SetPath(List<Transform> newPath)
    {
        waypoints    = newPath;
        currentIndex = 0;
        currentSpeed = 0f;
        SnapFacingToNextWaypoint();
    }

    public void Initialize(List<Transform> newPath,
                           MultiSpawnTrafficSpawner spawner,
                           bool isWrongLane)
    {
        currentIndex     = 0;
        currentSpeed     = 0f;
        _stoppedTimer    = 0f;
        _waitingAtSignal = null;
        _pendingJunction = null;

        if (isWrongLane) SetupWrongLane(newPath);
        else
        {
            waypoints    = new List<Transform>(newPath);
            state        = VehicleState.Normal;
            _isWrongLane = false;
        }

        SnapFacingToNextWaypoint();
    }
}