import Sim as sim
from sim.Sim_Part import src_part


jig1 = sim.Jig("Jig 1")
sim.BufferSource("SRC1", 10, 45, parent=jig1, getNextPart=sim.src_part("VB"))

buf = sim.RotBuffer("Buff", 3, 5, 5)

rob1 = sim.Rob("Robbie 1")
sim.RobHandling("Einlagern", jig1, buf, 5, 23, 5, parent=rob1)

jig2 = sim.Jig("Übergabe")
sim.BufferDrain(
    "Drain",
    62,
    parent=jig2,
)


rob2 = sim.Rob("Robbie 2")
sim.RobHandling("Auslagern", buf, jig2, 5, 56, 5, parent=rob2, take_from_position=3)

sim.core.run(0, 500)


sim.core.plotHistory(
    start_plot=50,
    end_plot=500,
)
