using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MultiSpawnTrafficSpawner : MonoBehaviour
{
    [Header("Vehicle Prefabs (all vehicle types)")]
    public List<GameObject> vehiclePrefabs;

    [Header("Spawn Points (drag CHILD spawn point objects here)")]
    public List<Transform> spawnPoints;

    [Header("Lane Parents for each Spawn Point (same order as spawnPoints)")]
    public List<Transform> laneParents;

    [Header("Population Control")]
    public int targetAliveVehicles = 25;

    [Header("Initial Burst")]
    public bool spawnOnStart = true;
    public int initialSpawnBurst = 8;

    [Header("Optional Wave Spawning")]
    public bool enableWaveSpawning = false;
    public float spawnInterval = 2.0f;
    public int vehiclesPerWave = 4;
    public bool uniqueSpawnPointsPerWave = true;

    [Header("Instant Respawn")]
    public bool respawnImmediatelyOnDestroy = true;

    [Header("Random Events")]
    [Range(0f, 0.30f)] public float wrongLaneChance = 0.06f;
    [Range(0f, 0.20f)] public float accidentChance = 0.02f;

    [Header("Speed Randomization")]
    public float speedMinMul = 0.85f;
    public float speedMaxMul = 1.15f;

    [Header("Spawn Safety")]
    public LayerMask vehicleLayer;
    public float spawnClearRadius = 1.2f;

    float timer = 0f;
    int alive = 0;
    int lastSpawnIndex = -1;
    private bool isShuttingDown = false;

    // ─────────────────────────────────────────────────────────────────────────

    void Start()
    {
        ValidateLists();
        if (!spawnOnStart) return;
        int initialCount = Mathf.Min(initialSpawnBurst, targetAliveVehicles);
        for (int i = 0; i < initialCount; i++)
            SpawnRandomIndex(true);
    }

    void Update()
    {
        if (!enableWaveSpawning) return;
        timer += Time.deltaTime;
        if (timer >= spawnInterval)
        {
            timer = 0f;
            SpawnWave();
        }
    }

    void OnDisable()         => isShuttingDown = true;
    void OnDestroy()         => isShuttingDown = true;
    void OnApplicationQuit() => isShuttingDown = true;

    // ─────────────────────────────────────────────────────────────────────────

    void ValidateLists()
    {
        if (vehiclePrefabs == null || vehiclePrefabs.Count == 0)
            Debug.LogError("[Spawner] vehiclePrefabs list is empty.");
        if (spawnPoints == null || spawnPoints.Count == 0)
            Debug.LogError("[Spawner] spawnPoints list is empty.");
        if (laneParents == null || laneParents.Count != spawnPoints.Count)
            Debug.LogError("[Spawner] laneParents must have SAME size/order as spawnPoints.");
    }

    bool CanSpawn()
    {
        if (isShuttingDown) return false;
        if (vehiclePrefabs == null || vehiclePrefabs.Count == 0) return false;
        if (spawnPoints == null || spawnPoints.Count == 0) return false;
        if (laneParents == null || laneParents.Count != spawnPoints.Count) return false;
        return true;
    }

    // ─────────────────────────────────────────────────────────────────────────

    void SpawnWave()
    {
        if (!CanSpawn()) return;
        int canSpawn = vehiclesPerWave;
        if (uniqueSpawnPointsPerWave)
            canSpawn = Mathf.Min(canSpawn, spawnPoints.Count);

        List<int> indices = new List<int>(spawnPoints.Count);
        for (int i = 0; i < spawnPoints.Count; i++) indices.Add(i);
        for (int i = indices.Count - 1; i > 0; i--)
        {
            int j = Random.Range(0, i + 1);
            (indices[i], indices[j]) = (indices[j], indices[i]);
        }
        for (int k = 0; k < canSpawn; k++)
            SpawnAtIndex(indices[k]);
    }

    void SpawnRandomIndex(bool preferDifferentFromLast)
    {
        if (!CanSpawn()) return;
        int idx = Random.Range(0, spawnPoints.Count);
        if (preferDifferentFromLast && spawnPoints.Count > 1)
        {
            for (int tries = 0; tries < 6; tries++)
            {
                if (idx != lastSpawnIndex) break;
                idx = Random.Range(0, spawnPoints.Count);
            }
        }
        lastSpawnIndex = idx;
        SpawnAtIndex(idx);
    }

    void SpawnAtIndex(int i)
    {
        if (!CanSpawn()) return;
        if (i < 0 || i >= spawnPoints.Count) return;

        Transform spawn      = spawnPoints[i];
        Transform laneParent = laneParents[i];
        if (spawn == null || laneParent == null) return;

        if (!IsSpawnClear(spawn.position))
        {
            StartCoroutine(RetrySpawn(i, 0.8f));
            return;
        }

        List<Transform> allWaypoints = GetWaypointsFromParent(laneParent);
        if (allWaypoints.Count == 0)
        {
            Debug.LogWarning($"[Spawner] Lane '{laneParent.name}' has no waypoints.");
            return;
        }

        int startIndex = GetClosestWaypointIndex(spawn.position, allWaypoints);

        List<Transform> waypoints = new List<Transform>();
        for (int w = startIndex; w < allWaypoints.Count; w++)
            waypoints.Add(allWaypoints[w]);

        if (waypoints.Count == 0)
        {
            Debug.LogWarning($"[Spawner] No waypoints after start index on '{laneParent.name}'.");
            return;
        }

        GameObject prefab = vehiclePrefabs[Random.Range(0, vehiclePrefabs.Count)];
        GameObject v      = Instantiate(prefab, spawn.position, spawn.rotation);

        Vector3 pos = v.transform.position;
        pos.z = 0f;
        v.transform.position = pos;

        alive++;
        v.AddComponent<OnDestroyCounter>().Init(this);

        var agent = v.GetComponent<VehicleAgent>();
        if (agent == null)
        {
            Debug.LogError($"[Spawner] Prefab '{prefab.name}' missing VehicleAgent!");
            Destroy(v);
            alive--;
            return;
        }

        bool isWrongLane = Random.value < wrongLaneChance;
        if (isWrongLane) waypoints.Reverse();

        agent.maxSpeed    *= Random.Range(speedMinMul, speedMaxMul);
        agent.vehicleLayer = vehicleLayer;

        // Random spawn delay — staggers vehicles so junction deadlocks
        // are prevented naturally before they can form
        float startDelay = Random.Range(0f, 1.5f);
        if (startDelay > 0.05f)
            StartCoroutine(DelayedInitialize(agent, waypoints,
                                             isWrongLane, startDelay));
        else
            agent.Initialize(waypoints, this, isWrongLane);

        // Separate if — not nested inside the else above
        if (Random.value < accidentChance)
            StartCoroutine(CrashLater(agent, Random.Range(2f, 8f)));
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Delayed initialize — staggers vehicle start to prevent junction deadlocks
    // ─────────────────────────────────────────────────────────────────────────

    IEnumerator DelayedInitialize(VehicleAgent agent, List<Transform> waypoints,
                                   bool isWrongLane, float delay)
    {
        yield return new WaitForSeconds(delay);
        if (agent != null)
            agent.Initialize(waypoints, this, isWrongLane);
    }

    // ─────────────────────────────────────────────────────────────────────────

    int GetClosestWaypointIndex(Vector3 spawnPos, List<Transform> wps)
    {
        int closest   = 0;
        float minDist = float.MaxValue;

        for (int i = 0; i < wps.Count; i++)
        {
            float dist = Vector3.Distance(spawnPos, wps[i].position);
            if (dist < minDist)
            {
                minDist = dist;
                closest = i;
            }
        }

        return closest;
    }

    // ─────────────────────────────────────────────────────────────────────────

    bool IsSpawnClear(Vector2 point)
    {
        Collider2D hit = Physics2D.OverlapCircle(point, spawnClearRadius,
                                                  vehicleLayer);
        return hit == null;
    }

    IEnumerator RetrySpawn(int index, float delay)
    {
        yield return new WaitForSeconds(delay);
        if (!isShuttingDown)
            SpawnAtIndex(index);
    }

    List<Transform> GetWaypointsFromParent(Transform parent)
    {
        List<Transform> list = new List<Transform>();
        for (int i = 0; i < parent.childCount; i++)
            list.Add(parent.GetChild(i));
        return list;
    }

    IEnumerator CrashLater(VehicleAgent agent, float delay)
    {
        yield return new WaitForSeconds(delay);
        if (agent != null) agent.SetCrashed();
    }

    // ─────────────────────────────────────────────────────────────────────────

    public void NotifyDestroyed()
    {
        if (isShuttingDown) return;
        alive = Mathf.Max(0, alive - 1);
        if (respawnImmediatelyOnDestroy && alive < targetAliveVehicles)
            SpawnRandomIndex(true);
    }

    void OnDrawGizmos()
    {
        if (spawnPoints == null) return;
        Gizmos.color = Color.green;
        foreach (var sp in spawnPoints)
            if (sp != null) Gizmos.DrawWireSphere(sp.position, 0.3f);
    }
}

// ─────────────────────────────────────────────────────────────────────────────

public class OnDestroyCounter : MonoBehaviour
{
    private MultiSpawnTrafficSpawner spawner;
    public void Init(MultiSpawnTrafficSpawner s) => spawner = s;

    void OnDestroy()
    {
        if (!Application.isPlaying)      return;
        if (spawner == null)             return;
        if (!spawner.isActiveAndEnabled) return;
        spawner.NotifyDestroyed();
    }
}