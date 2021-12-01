import sys

sys.path.append("D:/Projekte/Sim/src")
import sim
import timeit


bhf_sp = sim.Jig("Bahnhof SP")
sim.BufferSource("Log SP", 300, 60, parent=bhf_sp, getNextPart=sim.src_SLT_5)

bhf_ub = sim.LoadingStationIn("Bahnhof UB", 5)


# AGV-Kurs
course1 = sim.AgvCourse(["BHF SP", "BHF UB"], [180, 230])
agv1 = sim.AGV("AGV1", course1, "BHF SP")
agv2 = sim.AGV("AGV2", course1, "BHF UB")
sim.AgvDrive(
    "Drive 1",
    ["BHF SP", "BHF UB"],
    [sim.cond_agv_isFree("BHF UB"), sim.cond_buffer_empty(bhf_ub)],
    ["BHF SP"],
    [bhf_sp],
    ["BHF UB"],
    [bhf_ub],
    parent=agv1,
)
sim.AgvDrive(
    "Drive 2",
    ["BHF SP", "BHF UB"],
    [sim.cond_agv_isFree("BHF UB"), sim.cond_buffer_empty(bhf_ub)],
    ["BHF SP"],
    [bhf_sp],
    ["BHF UB"],
    [bhf_ub],
    parent=agv2,
)


rot_buffer = sim.RotBuffer("Drehspeicher", 3, 6, 5)

handling_jig = sim.Jig("Ablage")
sim.BufferDrain("Ende", 62, parent=handling_jig)

rb_110_100 = sim.Rob("110RB_100")
sim.RobHandlingBetter(
    "Entnahme",
    [
        sim.Pick(rot_buffer, time=50, position=3),
        sim.Place(handling_jig, time=10, timeto=2),
    ],
    parent=rb_110_100,
)

rb_100_100 = sim.Rob("100RB_100")
sim.RobHandling(
    "Einlagern", bhf_ub, rot_buffer, 10, 10, 15, parent=rb_100_100, place_at_position=0
)

start = timeit.timeit()
sim.core.run(0, 60 * 60)
end = timeit.timeit()
print(end - start)

sim.core.plotHistory()
