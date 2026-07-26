"""Journey Analytics Engine for generating business insights from customer journeys."""

from datetime import datetime, timezone
from app.stitching.models import CustomerJourney
from app.analytics.models import JourneyAnalytics, JourneyMetrics

class JourneyAnalyticsEngine:
    """Analyzes a unified customer journey and outputs actionable business insights."""

    def analyze(self, journey: CustomerJourney) -> JourneyAnalytics:
        if not journey.events:
            return JourneyAnalytics()

        # Sort events just in case
        events = sorted(journey.events, key=lambda e: e.timestamp)
        
        # 1. Calculate Metrics
        metrics = self._calculate_metrics(events)
        
        # 2. Apply Business Rules & Detect Friction
        friction_indicators, rule_outcomes = self._apply_business_rules(metrics, events)
        
        # 3. Detect Root Cause
        root_cause = self._detect_root_cause(friction_indicators)
        
        # 4. Determine Journey Status
        status = self._determine_status(events)
        
        # 5. Calculate Health Score
        health_score = self._calculate_health_score(metrics, friction_indicators, status)
        
        # 6. Generate Summary
        summary = self._generate_summary(status, metrics, root_cause)

        return JourneyAnalytics(
            journey_status=status,
            customer_health_score=health_score,
            metrics=metrics,
            friction_indicators=friction_indicators,
            business_rule_outcomes=rule_outcomes,
            root_cause=root_cause,
            summary=summary
        )

    def _calculate_metrics(self, events) -> JourneyMetrics:
        metrics = JourneyMetrics()
        metrics.total_events = len(events)
        metrics.channels_used = list({e.source for e in events})
        
        # Duration
        if len(events) > 1:
            duration = events[-1].timestamp - events[0].timestamp
            metrics.journey_duration_minutes = round(duration.total_seconds() / 60, 2)
            
        for e in events:
            # Simple keyword matching on event_type for demonstration
            etype = e.event_type.lower()
            if "support" in etype or "call" in etype:
                metrics.support_calls += 1
            if "payment" in etype and "fail" in etype:
                metrics.payment_failures += 1
            if "kyc" in etype and "fail" in etype:
                metrics.kyc_failures += 1
                
        return metrics

    def _apply_business_rules(self, metrics: JourneyMetrics, events) -> tuple[list[str], list[str]]:
        friction = []
        outcomes = []
        
        if metrics.payment_failures >= 3:
            friction.append("High Payment Risk")
            outcomes.append("Customer had 3 or more payment failures.")
        elif metrics.payment_failures > 0:
            friction.append("Payment Friction")
            
        if metrics.support_calls >= 2:
            friction.append("Customer Frustration")
            outcomes.append("Customer required multiple support contacts.")
            
        if metrics.kyc_failures > 0:
            friction.append("Verification Issue")
            outcomes.append("Customer failed KYC verification.")
            
        # Check inactivity (no events for 30 days)
        if events:
            last_event = events[-1]
            days_inactive = (datetime.now(timezone.utc) - last_event.timestamp).days
            if days_inactive >= 30:
                friction.append("Inactive Customer")
                outcomes.append("No activity for 30 days.")
                
        return friction, outcomes

    def _detect_root_cause(self, friction_indicators: list[str]) -> str | None:
        # Simple priority-based root cause selection
        priorities = [
            "Verification Issue",
            "High Payment Risk",
            "Customer Frustration",
            "Payment Friction",
            "Inactive Customer"
        ]
        for p in priorities:
            if p in friction_indicators:
                return p
        return None

    def _determine_status(self, events) -> str:
        last_type = events[-1].event_type.lower()
        if "submit" in last_type or "complete" in last_type or "success" in last_type:
            return "Completed"
        if "abandon" in last_type:
            return "Abandoned"
        return "Active"

    def _calculate_health_score(self, metrics: JourneyMetrics, friction: list[str], status: str) -> int:
        score = 100
        score -= (metrics.payment_failures * 10)
        score -= (metrics.support_calls * 5)
        score -= (metrics.kyc_failures * 15)
        
        if "Inactive Customer" in friction:
            score -= 20
            
        if status == "Completed":
            score += 10
        elif status == "Abandoned":
            score -= 30
            
        # Clamp between 0 and 100
        return max(0, min(100, score))

    def _generate_summary(self, status: str, metrics: JourneyMetrics, root_cause: str | None) -> str:
        base = f"Customer journey is {status.lower()}."
        issues = []
        if metrics.kyc_failures > 0:
            issues.append(f"{metrics.kyc_failures} KYC failure(s)")
        if metrics.payment_failures > 0:
            issues.append(f"{metrics.payment_failures} payment failure(s)")
        if metrics.support_calls > 0:
            issues.append(f"{metrics.support_calls} support interaction(s)")
            
        if issues:
            base += f" Encountered {' and '.join(issues)}."
        
        if root_cause:
            base += f" Primary friction point appears to be: {root_cause}."
            
        return base
