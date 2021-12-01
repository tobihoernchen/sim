import Sim as sim
import timeit


agv = sim.Jig("AGV-Bhf HC")
sim.BufferSource("HC-Einlauf", 60, 8, agv, getNextPart=sim.src_rework_10)

hc_rot1 = sim.RotBuffer("HC Drehspeicher 1", 3, 6, 5)
hc_rot2 = sim.RotBuffer("HC Drehspeicher 2", 3, 6, 5)

hc_drn = sim.Jig("HC Drain")
sim.BufferDrain("Hc Drain", 172, parent=hc_drn)

hand_special = sim.Jig("Handling Special")
hand_mess = sim.Jig("Handling Mess")

imt = sim.Jig("IMT")
sim.BufferWorkOn(
    "Messen",
    150,
    parent=imt,
    condition=sim.cond_inline,
    modifier=sim.mod_inline_measure,
)

na1 = sim.Jig("Nacharbeit 1")
sim.BufferWorkOn(
    "Nacharbeit",
    69,
    condition=sim.cond_rework,
    modifier=sim.mod_rework_done,
    parent=na1,
)

na2 = sim.Jig("Nacharbeit 2")
sim.BufferWorkOn(
    "Nacharbeit",
    69,
    condition=sim.cond_rework,
    modifier=sim.mod_rework_done,
    parent=na2,
)

aus_hc = sim.Buffer("Ausschleuse 1", 3)
sim.BufferWorkOn(
    "Ultraschall", 3000, condition=sim.cond_us, modifier=sim.mod_us_testing
)


verteiler = sim.Rob("Verteiler HC")
sim.RobHandlingConditional(
    "Verteilen",
    agv,
    [hand_mess, hand_special, hc_rot1, hc_rot2],
    conditions=[
        sim.cond_inline,
        lambda x: sim.cond_rework(x) or sim.cond_us(x),
        sim.cond_all,
    ],
    pick_dur=10,
    transport_durs=[15, 15, 20, 20],
    place_durs=[5, 5, 5, 5],
    places_at_position=[0, 0, 1, 5],
    parent=verteiler,
)
sim.RobHandlingConditional(
    "Aus Mess",
    hand_mess,
    [hc_rot1, hc_rot2],
    conditions=[sim.cond_all],
    pick_dur=5,
    transport_durs=[15, 15],
    place_durs=[5, 5],
    places_at_position=[1, 5],
    parent=verteiler,
)
sim.RobHandlingConditional(
    "Aus Specal",
    hand_special,
    [hc_rot1, hc_rot2],
    conditions=[sim.cond_all],
    pick_dur=5,
    transport_durs=[15, 15],
    place_durs=[5, 5],
    places_at_position=[1, 5],
    parent=verteiler,
)


abgabe_hc = sim.Rob("Abgabe HC")
sim.RobHandling(
    "Abgabe aus 1", hc_rot1, hc_drn, 5, 10, 5, parent=abgabe_hc, take_from_position=3
)
sim.RobHandling(
    "Abgabe aus 2", hc_rot1, hc_drn, 5, 10, 5, parent=abgabe_hc, take_from_position=2
)

sonder = sim.Rob("SonderRobbie")
sim.RobHandling("Mess hin", hand_mess, imt, 5, 20, 5, parent=sonder)
sim.RobHandling("Mess zurück", imt, hand_mess, 5, 20, 5, parent=sonder)
sim.RobHandling("Aus NA 1", na1, hand_special, 5, 15, 5, parent=sonder)
sim.RobHandling("Aus NA 2", na2, hand_special, 5, 15, 5, parent=sonder)

sim.RobHandling("Aus Ausschleuse", aus_hc, hand_special, 5, 20, 5, parent=sonder)
sim.RobHandlingConditional(
    "Aus Sonderablage",
    hand_special,
    [aus_hc, na1, na2],
    conditions=[sim.cond_us, sim.cond_all],
    pick_dur=5,
    transport_durs=[20, 15, 15],
    place_durs=[5, 5, 5],
    parent=sonder,
)


start = timeit.timeit()
sim.core.run(0, 60 * 60)
end = timeit.timeit()
print(end - start)

sim.core.plotHistory()
