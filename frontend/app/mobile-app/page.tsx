import { SimulatorPage } from "@/components/simulator-page";
import { getSimulatorChannel } from "@/lib/simulator-config";

const channel = getSimulatorChannel("mobile-app");

export default function MobileAppSimulatorRoute() {
  if (!channel) {
    throw new Error("Mobile app simulator configuration is missing.");
  }

  return <SimulatorPage channel={channel} />;
}
