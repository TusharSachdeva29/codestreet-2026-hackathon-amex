import Link from "next/link";

import { simulatorChannels } from "@/lib/simulator-config";

export default function HomePage() {
  return (
    <main className="landing-page">
      <section className="hero">
        <p className="eyebrow">American Express Cross-Channel Journey Stitching Platform</p>
        <h1>Phase 1 Event Simulator</h1>
        <p className="hero-copy">
          Generate realistic customer interaction events across website, mobile app, call centre,
          and physical store touchpoints. Each action sends one standardized payload to the backend API.
        </p>
      </section>

      <section className="channel-list">
        {simulatorChannels.map((channel) => (
          <Link
            key={channel.slug}
            className="channel-card"
            href={`/${channel.slug}`}
            style={{ ["--channel-accent" as string]: channel.accent }}
          >
            <span className="channel-kicker">{channel.source}</span>
            <h2>{channel.title}</h2>
            <p>{channel.description}</p>
            <strong>Open simulator</strong>
          </Link>
        ))}
      </section>
    </main>
  );
}
