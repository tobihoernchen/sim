import sys

sys.path.append("D:/Projekte/Sim/src")
import sim


jig1 = sim.Jig("Jig 1")
sim.BufferSource("SRC1", 10, 45, parent=jig1, getNextPart=sim.src_part("VB"))

buf = sim.RotBuffer("Buff", 3, 5, 5)

rob1 = sim.Rob("Robbie 1")
sim.RobHandlingBetter(
    "Einlagern", [sim.Pick(jig1, 5), sim.Place(buf, time=5, timeto=23)], parent=rob1
)

jig2 = sim.Jig("Übergabe")
sim.BufferDrain(
    "Drain",
    62,
    parent=jig2,
)


rob2 = sim.Rob("Robbie 2")
sim.RobHandlingBetter(
    "Auslagern",
    [sim.Pick(buf, 5, position=3), sim.Place(jig2, time=5, timeto=56)],
    parent=rob2,
)

print(sim.core.getAllTraces())
sim.core.run(0, 500)


sim.core.plotHistory(
    # start_plot=0,
    # end_plot=500,
)
print("fertig")
