"use client";

import { useState } from "react";

import type { SimulatorChannel } from "@/lib/simulator-config";

type FormState = {
  customerId: string;
  email: string;
  phoneNumber: string;
  cardLast4: string;
  deviceId: string;
  sessionId: string;
  cookieId: string;
  ipAddress: string;
  browserFingerprint: string;
  metadataValue: string;
};

type SimulatorPageProps = {
  channel: SimulatorChannel;
};

type EventResponse = {
  accepted: boolean;
  event_id: string;
  message: string;
};

const initialFormState: FormState = {
  customerId: "",
  email: "",
  phoneNumber: "",
  cardLast4: "",
  deviceId: "",
  sessionId: "",
  cookieId: "",
  ipAddress: "",
  browserFingerprint: "",
  metadataValue: ""
};

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export function SimulatorPage({ channel }: SimulatorPageProps) {
  const [selectedAction, setSelectedAction] = useState(channel.actions[0]);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const [statusMessage, setStatusMessage] = useState<string>("Ready to generate events.");
  const [responseBody, setResponseBody] = useState<EventResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function updateField<Key extends keyof FormState>(key: Key, value: FormState[Key]) {
    setFormState((current) => ({ ...current, [key]: value }));
  }

  async function handleSubmit() {
    setIsSubmitting(true);
    setStatusMessage(`Sending ${selectedAction.label} event to backend...`);

    const eventPayload = {
      event_id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      source: channel.source,
      event_type: selectedAction.eventType,
      identity: {
        customer_id: formState.customerId || null,
        email: formState.email || null,
        phone_number: formState.phoneNumber || null,
        card_last4: formState.cardLast4 || null,
        device_id: formState.deviceId || null,
        session_id: formState.sessionId || null,
        cookie_id: formState.cookieId || null,
        ip_address: formState.ipAddress || null,
        browser_fingerprint: formState.browserFingerprint || null
      },
      metadata: {
        action_label: selectedAction.label,
        channel_slug: channel.slug,
        note: formState.metadataValue || null
      }
    };

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/events`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(eventPayload)
      });

      const body = (await response.json()) as EventResponse;

      if (!response.ok) {
        throw new Error(body.message || "Backend request failed.");
      }

      setResponseBody(body);
      setStatusMessage(`${selectedAction.label} event sent successfully.`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unexpected error.";
      setResponseBody(null);
      setStatusMessage(`Failed to send event: ${message}`);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="simulator-shell" style={{ ["--channel-accent" as string]: channel.accent }}>
      <div className="simulator-header">
        <p className="eyebrow">Phase 1 Event Simulator</p>
        <h1>{channel.title}</h1>
        <p>{channel.description}</p>
      </div>

      <div className="simulator-grid">
        <div className="panel">
          <h2>Select Action</h2>
          <div className="action-grid">
            {channel.actions.map((action) => (
              <button
                key={action.eventType}
                className={action.eventType === selectedAction.eventType ? "action-card active" : "action-card"}
                onClick={() => setSelectedAction(action)}
                type="button"
              >
                <span>{action.label}</span>
                <small>{action.metadataHint}</small>
              </button>
            ))}
          </div>
        </div>

        <div className="panel">
          <h2>Identity Inputs</h2>
          <div className="field-grid">
            <label>
              Customer ID
              <input value={formState.customerId} onChange={(event) => updateField("customerId", event.target.value)} />
            </label>
            <label>
              Email
              <input
                type="email"
                value={formState.email}
                onChange={(event) => updateField("email", event.target.value)}
              />
            </label>
            <label>
              Phone Number
              <input
                value={formState.phoneNumber}
                onChange={(event) => updateField("phoneNumber", event.target.value)}
              />
            </label>
            <label>
              Card Last 4
              <input
                maxLength={4}
                value={formState.cardLast4}
                onChange={(event) => updateField("cardLast4", event.target.value.replace(/\D/g, ""))}
              />
            </label>
            <label>
              Device ID
              <input value={formState.deviceId} onChange={(event) => updateField("deviceId", event.target.value)} />
            </label>
            <label>
              Session ID
              <input value={formState.sessionId} onChange={(event) => updateField("sessionId", event.target.value)} />
            </label>
            <label>
              Cookie ID
              <input value={formState.cookieId} onChange={(event) => updateField("cookieId", event.target.value)} />
            </label>
            <label>
              IP Address
              <input value={formState.ipAddress} onChange={(event) => updateField("ipAddress", event.target.value)} />
            </label>
            <label>
              Browser Fingerprint
              <input value={formState.browserFingerprint} onChange={(event) => updateField("browserFingerprint", event.target.value)} />
            </label>
          </div>

          <label className="metadata-field">
            Metadata Note
            <textarea
              rows={4}
              placeholder={selectedAction.metadataHint}
              value={formState.metadataValue}
              onChange={(event) => updateField("metadataValue", event.target.value)}
            />
          </label>

          <button className="submit-button" disabled={isSubmitting} onClick={handleSubmit} type="button">
            {isSubmitting ? "Sending Event..." : `Send ${selectedAction.label} Event`}
          </button>
        </div>
      </div>

      <div className="panel response-panel">
        <h2>Backend Response</h2>
        <p className="status-message">{statusMessage}</p>
        <pre>{responseBody ? JSON.stringify(responseBody, null, 2) : "No response yet."}</pre>
      </div>
    </section>
  );
}
