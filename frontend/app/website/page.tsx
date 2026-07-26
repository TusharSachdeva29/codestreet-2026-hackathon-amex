import { SimulatorPage } from "@/components/simulator-page";
import { getSimulatorChannel } from "@/lib/simulator-config";

const channel = getSimulatorChannel("website");

export default function WebsiteSimulatorRoute() {
  if (!channel) {
    throw new Error("Website simulator configuration is missing.");
  }

  return <SimulatorPage channel={channel} />;
}
