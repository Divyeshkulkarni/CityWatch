using System.Collections.Generic;
using UnityEngine;

public class WaypointBranchParent : MonoBehaviour
{
    [Header("Option A (curve) waypoint parent")]
    public Transform optionA_WaypointParent;

    [Header("Option B (bridge) waypoint parent")]
    public Transform optionB_WaypointParent;

    [Range(0f, 1f)]
    public float chooseAProbability = 0.5f;

    public bool debugLogs = true;

    public List<Transform> PickRoute()
    {
        if (optionA_WaypointParent == null || optionB_WaypointParent == null)
        {
            if (debugLogs)
                Debug.LogWarning($"[Branch] Missing option parent on '{name}'. Assign OptionA and OptionB in Inspector.");
            return null;
        }

        bool chooseA = Random.value < chooseAProbability;
        Transform chosenParent = chooseA ? optionA_WaypointParent : optionB_WaypointParent;

        int count = chosenParent.childCount;
        if (count == 0)
        {
            if (debugLogs)
                Debug.LogWarning($"[Branch] Chosen route '{chosenParent.name}' has 0 waypoints (children). Add waypoint children.");
            return null;
        }

        List<Transform> route = new List<Transform>(count);
        for (int i = 0; i < count; i++)
            route.Add(chosenParent.GetChild(i));

        if (debugLogs)
            Debug.Log($"[Branch] At '{name}' chose {(chooseA ? "Option A" : "Option B")} => '{chosenParent.name}' ({count} waypoints).");

        return route;
    }
}