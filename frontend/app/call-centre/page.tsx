import { SimulatorPage } from "@/components/simulator-page";
import { getSimulatorChannel } from "@/lib/simulator-config";

const channel = getSimulatorChannel("call-centre");

export default function CallCentreSimulatorRoute() {
  if (!channel) {
    throw new Error("Call centre simulator configuration is missing.");
  }

  return <SimulatorPage channel={channel} />;
}
