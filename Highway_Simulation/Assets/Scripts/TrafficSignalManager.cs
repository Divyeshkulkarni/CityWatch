using System.Collections;
using UnityEngine;

public class TrafficSignalManager : MonoBehaviour
{
    [Header("Signals — assign in order A, B, C")]
    public TrafficSignal signalA;
    public TrafficSignal signalB;
    public TrafficSignal signalC;

    [Header("Timing")]
    public float greenDuration = 5f;

    void Start()
    {
        // Start with A green, B and C red
        SetSignals(true, false, false);
        StartCoroutine(CycleSignals());
    }

    IEnumerator CycleSignals()
    {
        while (true)
        {
            // Phase 1 — A green
            SetSignals(true, false, false);
            yield return new WaitForSeconds(greenDuration);

            // Phase 2 — B green
            SetSignals(false, true, false);
            yield return new WaitForSeconds(greenDuration);

            // Phase 3 — C green
            SetSignals(false, false, true);
            yield return new WaitForSeconds(greenDuration);
        }
    }

    void SetSignals(bool a, bool b, bool c)
    {
        if (signalA != null) signalA.SetGreen(a);
        if (signalB != null) signalB.SetGreen(b);
        if (signalC != null) signalC.SetGreen(c);
    }
}