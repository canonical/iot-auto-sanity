import schedule
import time
import threading
from sanity.agent.style import columns

class scheduler:

    WORK_FLAG = False
    last_line = 0

    def __init__(self, act):
        task = threading.Thread(target = self.schedule_task_runner)
        task.start()
        self.do_schedule(act)

    def schedule_task_runner(self):
        while True:
            schedule.run_pending()
            time.sleep(10)

    def wakeup_work(self):
        global WORK_FLAG
        WORK_FLAG = True
        print("====scheduled work start====".center(columns))


    def do_schedule(self, act):
        global WORK_FLAG

        if len(act) < 2:
            print("Wrong PERIODIC format")
            sys.exit()

        match act[1]:
            case "test":
                schedule.every().minute.do(self.wakeup_work)
            case "hour":
                schedule.every().hour.at(":00").do(self.wakeup_work)
            case "day":
                if len(act) < 3:
                    act.append("00:00")
                schedule.every().day.at(act[2]).do(self.wakeup_work)
            case "week":
                if len(act) < 3:
                    print("Wrong PERIODIC week format")
                    sys.exit()
                elif len(act) < 4:
                    act.append("00:00")

                match act[2]:
                    case "mon":
                        schedule.every().monday.at(act[3]).do(self.wakeup_work)
                    case "tue":
                        schedule.every().tuesday.at(act[3]).do(self.wakeup_work)
                    case "wed":
                        schedule.every().wednesday.at(act[3]).do(self.wakeup_work)
                    case "thu":
                        schedule.every().thursday.at(act[3]).do(self.wakeup_work)
                    case "fri":
                        schedule.every().friday.at(act[3]).do(self.wakeup_work)
                    case "sat":
                        schedule.every().saturday.at(act[3]).do(self.wakeup_work)
                    case "sun":
                        schedule.every().sunday.at(act[3]).do(self.wakeup_work)
                    case _:
                        print("unknown day "+ act[2])
                        sys.exit()
            case _:
                print("unknown setting" + act[1])
                sys.exit()


        WORK_FLAG = False
        while WORK_FLAG == False:
            print(("======== Current time: " + time.strftime("%Y-%m-%d  %H:%M") + "  Next job on: "  + str(schedule.next_run()) + " ========").center(columns), end="\r")
            time.sleep(30)
