export type SimulatorChannel = {
  slug: "website" | "mobile-app" | "call-centre" | "physical-store";
  source: "website" | "mobile_app" | "call_centre" | "physical_store";
  title: string;
  description: string;
  accent: string;
  actions: Array<{
    eventType: string;
    label: string;
    metadataHint: string;
  }>;
};

export const simulatorChannels: SimulatorChannel[] = [
  {
    slug: "website",
    source: "website",
    title: "Website Simulator",
    description:
      "Mimics browser-based customer actions such as applications, document uploads, and payment attempts.",
    accent: "var(--accent-website)",
    actions: [
      { eventType: "open_website", label: "Open Website", metadataHint: "landing page" },
      { eventType: "view_card", label: "View Card", metadataHint: "card product page" },
      { eventType: "compare_cards", label: "Compare Cards", metadataHint: "comparison page" },
      { eventType: "start_application", label: "Start Application", metadataHint: "application flow" },
      { eventType: "upload_documents", label: "Upload Documents", metadataHint: "verification step" },
      { eventType: "payment_attempt", label: "Payment Attempt", metadataHint: "payment amount" },
      { eventType: "logout", label: "Logout", metadataHint: "session end" }
    ]
  },
  {
    slug: "mobile-app",
    source: "mobile_app",
    title: "Mobile App Simulator",
    description:
      "Represents customer actions inside the mobile application across transactions, rewards, and card controls.",
    accent: "var(--accent-mobile)",
    actions: [
      { eventType: "login", label: "Login", metadataHint: "device model" },
      { eventType: "view_transactions", label: "View Transactions", metadataHint: "transaction range" },
      { eventType: "view_rewards", label: "View Rewards", metadataHint: "rewards section" },
      { eventType: "redeem_rewards", label: "Redeem Rewards", metadataHint: "reward category" },
      { eventType: "card_lock", label: "Card Lock", metadataHint: "lock reason" },
      { eventType: "card_unlock", label: "Card Unlock", metadataHint: "unlock reason" },
      { eventType: "logout", label: "Logout", metadataHint: "session end" }
    ]
  },
  {
    slug: "call-centre",
    source: "call_centre",
    title: "Call Centre Simulator",
    description:
      "Captures support interactions such as complaints, fraud reports, and customer enquiries.",
    accent: "var(--accent-call-centre)",
    actions: [
      { eventType: "authenticate_customer", label: "Authenticate Customer", metadataHint: "ivr or agent desk" },
      { eventType: "raise_complaint", label: "Raise Complaint", metadataHint: "complaint category" },
      { eventType: "payment_issue", label: "Payment Issue", metadataHint: "failed payment context" },
      { eventType: "card_lost", label: "Card Lost", metadataHint: "reported location" },
      { eventType: "fraud_report", label: "Fraud Report", metadataHint: "fraud concern" },
      { eventType: "general_enquiry", label: "General Enquiry", metadataHint: "topic summary" }
    ]
  },
  {
    slug: "physical-store",
    source: "physical_store",
    title: "Physical Store Simulator",
    description:
      "Models in-person card usage and service interactions such as purchases, refunds, and lounge access.",
    accent: "var(--accent-store)",
    actions: [
      { eventType: "card_swipe", label: "Card Swipe", metadataHint: "terminal id" },
      { eventType: "purchase", label: "Purchase", metadataHint: "purchase amount" },
      { eventType: "refund", label: "Refund", metadataHint: "refund amount" },
      { eventType: "reward_redemption", label: "Reward Redemption", metadataHint: "reward channel" },
      { eventType: "lounge_entry", label: "Lounge Entry", metadataHint: "lounge name" }
    ]
  }
];

export function getSimulatorChannel(slug: string): SimulatorChannel | undefined {
  return simulatorChannels.find((channel) => channel.slug === slug);
}
