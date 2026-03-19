using System.Collections.Generic;
using UnityEngine;

public class TrafficSignal : MonoBehaviour
{
    [Header("Signal State")]
    public bool isGreen = false;

    [Header("Custom Visual Objects")]
    [Tooltip("Drag your custom red signal object here")]
    public GameObject redLightObject;
    [Tooltip("Drag your custom green signal object here")]
    public GameObject greenLightObject;

    private List<VehicleAgent> _waitingVehicles = new List<VehicleAgent>();

    // ─────────────────────────────────────────────────────────────────────────

    void Start()
    {
        Collider2D col = GetComponent<Collider2D>();
        if (col != null) col.isTrigger = true;

        UpdateLightVisuals();
    }

    // ─────────────────────────────────────────────────────────────────────────

    public void SetGreen(bool green)
    {
        isGreen = green;
        UpdateLightVisuals();

        if (isGreen)
        {
            foreach (VehicleAgent v in _waitingVehicles)
            {
                if (v != null) v.SetSignalGreen();
            }
            _waitingVehicles.Clear();
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Simply shows or hides your custom objects
    // No color changes — your objects look exactly as designed
    // ─────────────────────────────────────────────────────────────────────────

    void UpdateLightVisuals()
    {
        if (redLightObject != null)
            redLightObject.SetActive(!isGreen);

        if (greenLightObject != null)
            greenLightObject.SetActive(isGreen);
    }

    // ─────────────────────────────────────────────────────────────────────────

    void OnTriggerEnter2D(Collider2D other)
    {
        VehicleAgent agent = other.GetComponent<VehicleAgent>();
        if (agent == null) return;
        if (agent.state == VehicleAgent.VehicleState.Crashed) return;

        if (!isGreen)
        {
            agent.SetSignalRed(this);
            _waitingVehicles.Add(agent);
        }
    }

    void OnTriggerExit2D(Collider2D other)
    {
        VehicleAgent agent = other.GetComponent<VehicleAgent>();
        if (agent == null) return;
        _waitingVehicles.Remove(agent);
    }
}
// ```

// ---

// ## Step 3 — Setup in Inspector

// For each Signal (SignalA, SignalB, SignalC):

// 1. Click the Signal GameObject
// 2. Find **Traffic Signal** component
// 3. Assign:
// ```
// Red Light Object    →  drag your custom red signal object here
// Green Light Object  →  drag your custom green signal object here