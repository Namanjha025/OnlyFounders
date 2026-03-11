import enum


class UserRole(str, enum.Enum):
    FOUNDER = "founder"
    ADVISOR = "advisor"
    INVESTOR = "investor"
    ADMIN = "admin"


class StartupStage(str, enum.Enum):
    IDEA = "idea"
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    GROWTH = "growth"


class Industry(str, enum.Enum):
    SAAS = "saas"
    FINTECH = "fintech"
    HEALTHTECH = "healthtech"
    EDTECH = "edtech"
    ECOMMERCE = "ecommerce"
    AI_ML = "ai_ml"
    BIOTECH = "biotech"
    CLEANTECH = "cleantech"
    HARDWARE = "hardware"
    MARKETPLACE = "marketplace"
    MEDIA = "media"
    GAMING = "gaming"
    ENTERPRISE = "enterprise"
    CONSUMER = "consumer"
    OTHER = "other"


class BusinessModel(str, enum.Enum):
    SAAS = "saas"
    MARKETPLACE = "marketplace"
    ECOMMERCE = "ecommerce"
    SUBSCRIPTION = "subscription"
    TRANSACTIONAL = "transactional"
    FREEMIUM = "freemium"
    AD_SUPPORTED = "ad_supported"
    HARDWARE = "hardware"
    LICENSING = "licensing"
    OTHER = "other"


class TargetMarket(str, enum.Enum):
    B2B = "b2b"
    B2C = "b2c"
    B2B2C = "b2b2c"
    B2G = "b2g"
    D2C = "d2c"


class ProductStage(str, enum.Enum):
    IDEA = "idea"
    PROTOTYPE = "prototype"
    MVP = "mvp"
    BETA = "beta"
    LIVE = "live"


class FundingRoundType(str, enum.Enum):
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    CONVERTIBLE_NOTE = "convertible_note"
    SAFE = "safe"
    GRANT = "grant"
    OTHER = "other"


class DocumentCategory(str, enum.Enum):
    PITCH_DECK = "pitch_deck"
    CAP_TABLE = "cap_table"
    FINANCIALS = "financials"
    INCORPORATION = "incorporation"
    BUSINESS_PLAN = "business_plan"
    TERM_SHEET = "term_sheet"
    SAFE_AGREEMENT = "safe_agreement"
    PATENT = "patent"
    CONTRACT = "contract"
    OTHER = "other"


class MemberRole(str, enum.Enum):
    FOUNDER = "founder"
    COFOUNDER = "cofounder"
    CTO = "cto"
    CPO = "cpo"
    CFO = "cfo"
    ADVISOR = "advisor"
    EMPLOYEE = "employee"


class IncorporationType(str, enum.Enum):
    C_CORP = "c_corp"
    S_CORP = "s_corp"
    LLC = "llc"
    LLP = "llp"
    PBC = "pbc"
    LTD = "ltd"
    OTHER = "other"
