using System.Collections.Generic;
using UnityEngine;

public class JunctionYield : MonoBehaviour
{
    // All vehicles currently inside this junction
    private HashSet<int> _vehiclesInside = new HashSet<int>();

    // ─────────────────────────────────────────────────────────────────────────

    void Start()
    {
        // Make sure collider is set as trigger
        Collider2D col = GetComponent<Collider2D>();
        if (col != null) col.isTrigger = true;
    }

    // ─────────────────────────────────────────────────────────────────────────

    public bool IsJunctionClear(GameObject requestingVehicle)
    {
        // Junction is clear if empty OR only this vehicle is inside
        if (_vehiclesInside.Count == 0) return true;
        if (_vehiclesInside.Count == 1 &&
            _vehiclesInside.Contains(requestingVehicle.GetInstanceID()))
            return true;
        return false;
    }

    // ─────────────────────────────────────────────────────────────────────────

    void OnTriggerEnter2D(Collider2D other)
    {
        VehicleAgent agent = other.GetComponent<VehicleAgent>();
        if (agent == null) return;
        if (agent.state == VehicleAgent.VehicleState.Crashed) return;

        _vehiclesInside.Add(other.gameObject.GetInstanceID());
    }

    void OnTriggerExit2D(Collider2D other)
    {
        _vehiclesInside.Remove(other.gameObject.GetInstanceID());
    }
}