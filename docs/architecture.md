# LIMBUZZ V1 Architecture

This document translates the V1 product requirements into an implementation-level architecture. It is intentionally limited to the controlled Android pilot.

## Architecture principles

- The emergency path is local-first and must not depend on internet access.
- Emergency SMS is sent by the device through the native Android SMS stack.
- SMS dispatch happens before the primary-contact call.
- An active emergency is a persisted session owned by an Android foreground service.
- Location and audio are used only during an active emergency.
- Firebase is optional authentication infrastructure, not a dependency of the emergency path.
- No V1 application backend, gateway SMS, push notification service, or cloud media storage.

## 1. V1 system context

```mermaid
flowchart LR
    User((User))
    Contacts((Emergency contacts))
    Carriers[Cellular carriers\nSMS and voice]
    Maps[Map provider\nlink opened by recipient]
    Firebase[Firebase Auth\noptional Google Sign-In]

    subgraph Device[Android device]
        App[LIMBUZZ Flutter app]
        Native[Native Android adapters]
        Store[(Local database\ncontacts, sessions, actions)]
        Files[(Private local files\naudio recordings)]
        FGS[Android foreground service\npersistent emergency session]
        Location[Android location services]
        SMS[Android SMS manager]
        Phone[Android dialer / call manager]
        Audio[Android microphone]
    end

    User --> App
    App <--> Native
    App <--> Store
    App <--> Files
    App --> FGS
    FGS <--> Store
    Native --> Location
    Native --> SMS
    Native --> Phone
    Native --> Audio
    Location -. map URL .-> SMS
    SMS --> Carriers
    Phone --> Carriers
    Carriers --> Contacts
    Contacts --> Maps
    App -. optional sign-in .-> Firebase
    App --> User
```

### System boundary

The Flutter application owns screens, validation, the SOS state machine, orchestration, and user-visible status. Native Android adapters own platform capabilities that Flutter cannot guarantee by itself: SMS dispatch, calls, location, microphone access, foreground-service lifecycle, reboot restoration, and permission state.

The cellular network is the emergency transport. Firebase is outside the critical path and may be unreachable, unavailable, or unused.

## 2. SOS emergency sequence

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Flutter UI
    participant Session as Foreground service
    participant DB as Local database
    participant Location as Android location
    participant Audio as Android microphone
    participant SMS as Native SMS
    participant Carrier as Cellular network
    participant Contacts as Emergency contacts
    participant Call as Native phone

    User->>UI: Press and hold SOS
    UI-->>User: Show 3-second progress
    alt Released before 3 seconds
        User->>UI: Release
        UI-->>User: Abort with no side effects
    else Hold completes
        UI->>Session: Start emergency session
        Session->>DB: Persist ACTIVE state
        Session->>Audio: Start local recording if permitted
        Session->>Location: Request immediate fix
        par Dispatch emergency SMS
            Session->>SMS: Send to all configured contacts
            SMS->>Carrier: Device-side SMS
            Carrier-->>Contacts: Emergency message
            SMS-->>Session: Per-contact sent/failed status
            Session->>DB: Persist each action outcome
        and Wait for location, max 10 seconds
            Location-->>Session: Best available fix or timeout
        end
        Session-->>UI: Show per-contact status and location state
        Session->>Call: Dial primary contact after SMS dispatch
        Call->>Carrier: Voice call
        Carrier-->>Contacts: Primary-contact call
        Session->>DB: Persist call outcome
    end

    opt Better location arrives after first SMS
        Location-->>Session: Materially better fix
        Session->>SMS: Send one optional follow-up SMS
        SMS->>Carrier: Device-side SMS
        Carrier-->>Contacts: Updated location
        Session->>DB: Persist follow-up outcome
    end

    opt User cancels
        User->>UI: Cancel active SOS
        UI->>Session: End emergency session
        Session->>Audio: Stop recording
        Session->>SMS: Send all-clear to alerted contacts
        SMS->>Carrier: Device-side SMS
        Carrier-->>Contacts: False alarm / safe message
        Session->>DB: Persist CLOSED state and outcomes
        Session-->>UI: Show completed all-clear status
    end
```

### Important runtime rules

1. Releasing the control before three seconds does nothing.
2. Location collection never blocks the first SMS; ten seconds is the maximum wait.
3. The first SMS is dispatched before the primary-contact call.
4. Each contact gets an independent retry schedule: immediately, after 15 seconds, and after 45 seconds.
5. Any one failure is recorded and shown without stopping the rest of the sequence.
6. Cancel sends an all-clear to every contact already alerted, without a confirmation prompt.
7. Every state transition and action result is persisted so force-close and reboot recovery can resume safely.

## 3. Local data model

```mermaid
erDiagram
    USER_PROFILE {
        string id PK
        string google_subject UK "nullable"
        datetime created_at
        datetime updated_at
    }

    EMERGENCY_CONTACT {
        string id PK
        string user_profile_id FK "nullable for guest"
        string name
        string phone_number
        string relationship
        boolean is_primary
        datetime created_at
        datetime updated_at
    }

    EMERGENCY_SESSION {
        string id PK
        string user_profile_id FK "nullable for guest"
        string state "ACTIVE or CLOSED"
        string activation_source
        datetime started_at
        datetime ended_at
        string end_reason
        string latest_latitude "nullable"
        string latest_longitude "nullable"
        string latest_accuracy "nullable"
    }

    SESSION_ACTION {
        string id PK
        string session_id FK
        string contact_id FK "nullable"
        string action_type "SMS, CALL, LOCATION, AUDIO, ALL_CLEAR"
        string status "PENDING, SENT, FAILED, SKIPPED"
        integer attempt_count
        string error_code "nullable"
        datetime attempted_at
        datetime completed_at "nullable"
    }

    AUDIO_RECORDING {
        string id PK
        string session_id FK
        string local_path
        integer size_bytes
        integer duration_seconds
        datetime recorded_at
        datetime retention_prompted_at "nullable"
        datetime deleted_at "nullable"
    }

    USER_PROFILE o|--o{ EMERGENCY_CONTACT : owns
    USER_PROFILE o|--o{ EMERGENCY_SESSION : starts
    EMERGENCY_SESSION ||--o{ SESSION_ACTION : records
    EMERGENCY_CONTACT o|--o{ SESSION_ACTION : receives
    EMERGENCY_SESSION ||--o{ AUDIO_RECORDING : contains
```

### Persistence notes

- `user_profile_id` remains nullable so guest mode is a first-class state.
- Contacts and sessions are readable without connectivity.
- Audio files remain in app-private device storage until the user explicitly shares or deletes one.
- The database is the source of truth for recovery; in-memory state is only a live projection for the UI.
- A future sign-in links existing guest data instead of replacing it.

## 4. Build boundary for V1

```mermaid
flowchart TB
    subgraph V1[Build in V1]
        UI[Flutter screens]
        State[SOS state machine]
        DB[Local database]
        Platform[Android platform adapters]
        FGS[Foreground service]
        Auth[Optional Firebase Google Sign-In]
        QA[Physical-device field testing]
    end

    subgraph Later[Explicitly outside V1]
        Backend[Application backend]
        Gateway[Africa's Talking gateway SMS]
        Push[FCM push notifications]
        History[Notification history]
        Cloud[Cloud backup and media storage]
        Social[Usernames and social discovery]
    end

    UI --> State --> Platform
    State --> DB
    Platform --> FGS
    UI -. optional .-> Auth
    QA --> UI
    QA --> Platform
    Backend -. deferred .-> Gateway
    Backend -. deferred .-> Push
    Backend -. deferred .-> History
    Backend -. deferred .-> Cloud
    Backend -. deferred .-> Social
```

## 5. Open implementation decisions

- Select and validate the Flutter local database package against API 24 and low-end devices.
- Decide the audio storage cap before implementing the recording feature.
- Finalize emergency and all-clear message copy before SMS implementation.
- Create and back up the Android release keystore; register development and release SHA-1 fingerprints with Firebase.
- Confirm Android OEM behavior for foreground-service permissions, reboot receivers, SMS, calls, and battery optimization.
