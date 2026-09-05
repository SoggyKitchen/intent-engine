"""
Single source of truth for SaaSpare's schema.org entity identity.

Why this file exists
--------------------
On 2026-09-06 an audit found FOUR different `sameAs` arrays shipping across the
site (418 + 23 + 5 + 1 pages), and the dominant one listed:

    https://www.linkedin.com/company/saaspare   -> HTTP 404
    https://twitter.com/saaspare  /  https://x.com/saaspare  -> unverifiable
    https://www.crunchbase.com/organization/saaspare -> unverifiable

The identical array is published by the competitor saaspare.com in THEIR
Organization schema. `sameAs` is an identity assertion: publishing profile URLs
we cannot prove we own, that 404, and that a different domain also claims,
gives Google contradictory evidence about which site the "SaaSpare" entity is.
That is consistent with the measured Brand Signal of 0.

Rule: `sameAs` contains only references we can VERIFY.

ABN 20 602 197 525 is verified live on the Australian Business Register as
"VON PAPEN, KAYLAN", Individual/Sole Trader, active, QLD 4220. It is a
government registry record, not a claim, and no competitor can assert it.

To add a profile back, it must first exist AND be owned by us.
"""

ORG_ID = "https://saaspare.org/#organization"
SITE_ID = "https://saaspare.org/#website"
PERSON_ID = "https://saaspare.org/authors/kaylan-von-papen#person"

ABN = "20602197525"
ABN_LOOKUP = f"https://abr.business.gov.au/ABN/View?abn={ABN}"

# VERIFIED references only. Do not add an entry without a passing check.
ORG_SAME_AS = [ABN_LOOKUP]
PERSON_SAME_AS = [ABN_LOOKUP]

ORG_NAME = "SaaSpare"
ORG_URL = "https://saaspare.org/"

# Kept deliberately free of a tool/page count so a corpus change cannot turn
# this string into a false claim. Counts belong in generated copy, not identity.
ORG_DESCRIPTION = (
    "Independent B2B SaaS comparison publisher. Source-linked pricing, "
    "documented methodology, and disclosed affiliate relationships."
)


def organization() -> dict:
    return {
        "@type": "Organization",
        "@id": ORG_ID,
        "name": ORG_NAME,
        "url": ORG_URL,
        "description": ORG_DESCRIPTION,
        "logo": {
            "@type": "ImageObject",
            "url": "https://saaspare.org/favicon-512.png",
            "width": 512,
            "height": 512,
        },
        "foundingDate": "2026-04-18",
        "areaServed": "Worldwide",
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "ABN",
            "value": ABN,
        },
        "founder": {"@id": PERSON_ID},
        "publishingPrinciples": "https://saaspare.org/editorial-policy",
        "knowsAbout": [
            "B2B SaaS", "Software Pricing", "CRM", "SEO Tools",
            "Dev Tools", "HR Software", "Finance Operations",
        ],
        "sameAs": ORG_SAME_AS,
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "Editorial",
            "email": "hellothere@saaspare.org",
            "areaServed": "Worldwide",
            "availableLanguage": ["English"],
        },
    }
