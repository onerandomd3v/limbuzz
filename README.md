# LIMBUZZ

LIMBUZZ is an Android-focused personal-safety project. Its V1 is designed around a dependable, device-local SOS path: a person can alert trusted contacts even when the app has no internet connection.

## V1 emergency experience

- Hold the SOS control for three seconds to activate; releasing early has no side effects.
- Persist an active emergency session in an Android foreground service so the app can recover after a force-close or reboot.
- Dispatch device-side SMS to every configured emergency contact before calling the primary contact.
- Collect location in parallel without delaying the first alert; send without a location fix after the timeout.
- Record audio locally when permission is available, show per-contact delivery status, and retry failed SMS attempts.
- On cancellation, send an all-clear to every contact already alerted and close the session safely.

## Architecture

The V1 architecture, runtime rules, data model, and diagram exports are documented in [docs/architecture.md](docs/architecture.md).

It includes:

- a system-context Mermaid diagram and local data-model Mermaid diagram;
- an SOS state flow for the simple user-visible progression;
- a companion swimlane showing service, Android, and contact handoffs; and
- the V1 build boundary separating the device-local emergency path from deferred cloud features.

The SVG diagrams have editable, self-contained HTML sources in `docs/diagrams/` where applicable.

## V1 scope boundary

The critical emergency path does not depend on a LIMBUZZ backend, gateway SMS, push notifications, cloud media storage, or sign-in. Firebase may support optional authentication, but it is not required to activate or run SOS.
