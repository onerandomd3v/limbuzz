# LIMBUZZ

LIMBUZZ is an Android-first, cross-platform personal-safety project. Its V1 uses React Native, Expo, and TypeScript for the shared app layer, with Kotlin/native Android integrations behind a typed Emergency Platform Layer. The app is built with Expo Development Builds, while future Swift/iOS integrations can implement the same platform contract later.

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
- an icon-assisted system-context SVG companion showing the mobile platform boundary;
- an SOS state flow for the simple user-visible progression;
- a companion swimlane showing service, Android, and contact handoffs; and
- the V1 build boundary separating the device-local emergency path from deferred cloud features.

The SVG diagrams have editable, self-contained HTML sources in `docs/diagrams/` where applicable.

## V1 scope boundary

The critical emergency path does not depend on a backend, gateway SMS, push notifications, cloud media storage, or sign-in. A future Backend API remains technology TBD behind a typed API boundary and outside offline SOS. Device-side SMS, calls, location, foreground-session recovery, and local audio remain platform capabilities owned by the Emergency Platform Layer.

## Development workflow

Expo Go is useful for early UI experiments, but LIMBUZZ uses Expo Development Builds for real development because the emergency platform requires custom Kotlin/native Android modules and will later require Swift/native iOS modules. A Development Build is a custom app binary with those native capabilities included; the shared React Native and TypeScript code still supports fast refresh. EAS Build or local native builds can compile the platform-specific app artifacts.
