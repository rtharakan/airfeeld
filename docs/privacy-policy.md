# Privacy Policy

**Effective Date**: 2026-01-31  
**Last Updated**: 2026-01-31

Airfeeld is a privacy-preserving aviation guessing game built with privacy as a core design principle, not an afterthought.

## Data Collection

### What We Collect

**Player Profile:**
- Username (your choice, no real name required)
- Total score
- Games played count

**Gameplay Data:**
- Game round history (photo shown, guesses submitted, scores)
- Timestamps of game rounds

**Photo Uploads:**
- Image file (EXIF metadata stripped)
- Airport association
- Optional attribution (photographer name, license)

### What We DO NOT Collect

- Email addresses
- Phone numbers
- Device identifiers or fingerprints
- IP addresses (except transient server logs)
- Precise location or location history
- Behavioral analytics or profiling data
- Social connections or friend lists
- Browsing patterns or engagement metrics
- Third-party tracking cookies

## How We Use Data

**Gameplay:**
- Display photos to players (EXIF stripped)
- Calculate scores based on guesses
- Update leaderboards

**Photo Management:**
- Store user-contributed photos for gameplay
- Display photographer attribution (if provided)

**System Maintenance:**
- Monitor API health
- Debug errors (without personal data correlation)

## How We DO NOT Use Data

- No behavioral profiling or user tracking
- No targeted advertising or marketing
- No data sales or sharing with third parties
- No engagement optimization or A/B testing
- No social graph building or relationship inference

## Data Storage

**Location**: Self-hosted servers (no third-party cloud providers with data mining)

**Retention**:
- Player profiles: Retained indefinitely (deletion available on request)
- Game history: Retained for leaderboard calculation, archivable after 90 days
- Photo uploads: Retained indefinitely as public game content
- Server logs: Rotated after 7 days

**Security**:
- SQLite database with file-level encryption
- HTTPS for all API communication
- Regular security audits

## EXIF Metadata Stripping

All uploaded photos undergo mandatory EXIF stripping:

1. Photo uploaded to server
2. Pillow library removes all metadata (GPS, timestamps, device info)
3. Verification step ensures complete removal
4. Only then is photo stored

**If verification fails, upload is rejected.** We never store unverified photos.

## Third-Party Services

**None.** Airfeeld does not use:

- Analytics services (Google Analytics, Mixpanel, etc.)
- Advertising networks
- Social media integrations
- CDNs with tracking capabilities
- Cloud providers with data mining practices

## Open Data Sources

Aviation data comes from open, publicly available sources:

- **Airports**: [OurAirports](https://ourairports.com/) (CC0)
- **Airlines**: [OpenFlights](https://openflights.org/) (ODbL)
- **Aircraft**: [OpenSky Network](https://opensky-network.org/) (CC BY-SA 4.0)

No proprietary or scraped data is used.

## User Rights

**Access**: View your player profile and game history  
**Deletion**: Request complete account and data deletion  
**Portability**: Export your data in JSON format  
**Correction**: Update your username (one-time change allowed)

To exercise these rights, open an issue on GitHub or contact via the repository.

## Children's Privacy

Airfeeld does not knowingly collect data from children under 13. No age verification is required, as minimal data collection makes the service inherently safer for all ages.

## Changes to Privacy Policy

Updates to this policy will be:

1. Committed to the repository with clear changelog
2. Announced in release notes
3. Effective 30 days after publication

Continued use after changes constitutes acceptance.

## Jurisdiction

This service operates under principles of data minimization and privacy by design, regardless of jurisdiction. We comply with:

- GDPR (European Union)
- CCPA (California)
- Privacy Act (Australia)
- PIPEDA (Canada)

## Audits

This privacy policy and all data practices are auditable:

- Source code is open source (MIT license)
- Data flows documented in [specs/001-aviation-games/spec.md](../specs/001-aviation-games/spec.md)
- Implementation plan in [specs/001-aviation-games/plan.md](../specs/001-aviation-games/plan.md)

External privacy audits welcome.

## Contact

For privacy concerns, open an issue on GitHub or contact the maintainers.

---

**Commitment**: Airfeeld will never compromise privacy for engagement, monetization, or growth. Privacy is a constraint, not a feature.
