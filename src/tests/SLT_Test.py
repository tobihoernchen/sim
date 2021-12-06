import sys

sys.path.append("D:/Projekte/Sim/src")
import sim


LS = sim.LoadingStationIn("LS")
sim.BufferSource("SLT-Source", 300, 60, parent=LS, getNextPart=sim.src_SLT(5))


buf = sim.Jig("Abgabe")
sim.BufferDrain("Systemgrenze", 68, buf)

rob = sim.Rob("Robert")
sim.RobHandlingBetter("Unload", [sim.Pick(LS, 10), sim.Place(buf, 10, 20)], rob)


sim.core.run(0, 60 * 60)
sim.core.plotHistory()
