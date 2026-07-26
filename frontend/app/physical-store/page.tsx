import { SimulatorPage } from "@/components/simulator-page";
import { getSimulatorChannel } from "@/lib/simulator-config";

const channel = getSimulatorChannel("physical-store");

export default function PhysicalStoreSimulatorRoute() {
  if (!channel) {
    throw new Error("Physical store simulator configuration is missing.");
  }

  return <SimulatorPage channel={channel} />;
}
