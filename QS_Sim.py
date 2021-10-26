
import Sim_Tools as sim


core = sim.simCore(0,50)
part = "Bauteil"
bf1 = sim.buffer("Buffer 1", 3, [part])
bf2 = sim.buffer("Buffer 2", 3, [])
rob = sim.rob("Rob")
h1 = sim.rob_handling_program("H1", 10, bf1, bf2)
h2 = sim.rob_handling_program("H2", 10, bf2, bf1)

rob.add_programm(h1)
rob.add_programm(h2)


core.addObject(bf1)
core.addObject(bf2)
core.addObject(rob)

core.run()

core.plotHistory()



