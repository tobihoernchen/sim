import sys

sys.path.append("D:/Projekte/Sim/src")
import sim


jig11 = sim.Jig("Jig 11")
sim.BufferSource("SRC1", 10, 45, parent=jig11, getNextPart=sim.src_part("VB"))

jig12 = sim.Jig("Jig 12")
sim.BufferSource("SRC2", 10, 41, parent=jig12, getNextPart=sim.src_part("HC"))


geo = sim.Geo("Geo", ["VB", "HC"], "Z1", 25)

rob11 = sim.Rob("Robbie 11")
sim.RobHandling("Einlagern", jig11, geo, 5, 23, 5, parent=rob11)
rob12 = sim.Rob("Robbie 12")
sim.RobHandling("Einlagern", jig12, geo, 5, 20, 5, parent=rob12)

jig2 = sim.Jig("Übergabe")
sim.BufferDrain(
    "Drain",
    62,
    parent=jig2,
)


rob2 = sim.Rob("Robbie 2")
sim.RobHandling("Auslagern", geo, jig2, 5, 56, 5, parent=rob2, take_from_position=3)

print(sim.core.getAllTraces())
sim.core.run(0, 500)


sim.core.plotHistory(
    # start_plot=0,
    # end_plot=500,
)
print("fertig")
