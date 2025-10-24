# ML Data Collection & Labeling Guidelines

## Table of Contents

1. [Overview](#overview)
2. [Data Diversity Requirements](#data-diversity-requirements)
3. [Label Taxonomy](#label-taxonomy)
4. [Labeling Instructions](#labeling-instructions)
5. [Privacy & Consent Framework](#privacy--consent-framework)
6. [Recommended Tools](#recommended-tools)
7. [Quality Assurance](#quality-assurance)
8. [Data Management](#data-management)

---

## Overview

This document provides comprehensive guidelines for collecting, organizing, and labeling training data for the Haski ML pipeline. High-quality, diverse, and properly labeled data is critical for building accurate and fair skin/hair analysis models.

**Key Principles:**

- ✅ **Diversity**: Collect data across all demographic groups
- ✅ **Transparency**: Clear labeling and metadata tracking
- ✅ **Privacy**: Strong consent and data protection
- ✅ **Quality**: Strict quality standards for all data
- ✅ **Documentation**: Comprehensive metadata collection

---

## Data Diversity Requirements

### 1. Skin Tone Diversity

**Critical**: ML models trained on homogeneous skin tones show significantly reduced accuracy on other tones. This is a well-documented issue in medical AI.

**Target Distribution:**

| Fitzpatrick Scale   | Coverage Target | Notes                            |
| ------------------- | --------------- | -------------------------------- |
| Type I (Very Fair)  | 15%             | Light skin, minimal pigmentation |
| Type II (Fair)      | 15%             | Fair skin, sometimes freckles    |
| Type III (Medium)   | 20%             | Medium/olive skin tone           |
| Type IV (Tan)       | 20%             | Darker medium skin tone          |
| Type V (Deep)       | 15%             | Deep skin tone                   |
| Type VI (Very Deep) | 15%             | Very deep skin tone              |

**Why this matters:**

- Models perform better on skin tones they're trained on
- 20% accuracy gap common between tone groups
- Balanced training → fairer results for all users

**Action items:**

- Recruit diverse dataset contributors
- Document Fitzpatrick type for each image
- Monitor per-tone accuracy during evaluation
- Flag models with >5% tone-based accuracy gap

### 2. Age Range Diversity

**Target Distribution:**

| Age Group | Coverage Target | Key Characteristics            |
| --------- | --------------- | ------------------------------ |
| 13-18     | 10%             | Teenage skin/hair changes      |
| 19-25     | 15%             | Young adult, transition period |
| 26-35     | 25%             | Prime adult range              |
| 36-45     | 20%             | Mature skin changes            |
| 46-55     | 15%             | Aging-related changes          |
| 56-65     | 10%             | Senior skin/hair               |
| 65+       | 5%              | Very senior demographics       |

**Challenges:**

- Harder to recruit older demographic
- Ethical considerations with consent
- Different skin characteristics per age group

**Action items:**

- Stratified sampling to ensure coverage
- Document age range (not exact age for privacy)
- Analyze model performance per age group

### 3. Gender & Biological Sex Diversity

**Target Distribution:**

| Category      | Coverage Target | Notes                                         |
| ------------- | --------------- | --------------------------------------------- |
| Male          | 40%             | Different hair/skin patterns                  |
| Female        | 40%             | Different cosmetic products, hormonal factors |
| Non-binary    | 10%             | Often underrepresented                        |
| Not disclosed | 10%             | Respect privacy preferences                   |

**Why this matters:**

- Facial hair patterns differ by sex
- Hormonal acne patterns differ
- Cosmetic use patterns differ
- Model must work fairly for all

**Action items:**

- Equal representation target
- Document reported gender (not assigned)
- Analyze per-gender fairness metrics

### 4. Lighting Conditions

**Critical for real-world deployment** (users take photos under many conditions):

| Lighting Type                 | Coverage Target | Description                         |
| ----------------------------- | --------------- | ----------------------------------- |
| Natural outdoor (daylight)    | 30%             | Bright outdoor lighting             |
| Window/indirect natural       | 25%             | Indoor near window                  |
| Warm indoor (incandescent)    | 20%             | Typical home lighting (yellow-ish)  |
| Cool indoor (LED/fluorescent) | 15%             | Office/bathroom lighting (blue-ish) |
| Artificial flash              | 10%             | Flash photography (harsh shadows)   |

**Challenges:**

- Lighting dramatically affects skin appearance
- Color casts can confuse models
- Mobile flash particularly problematic

**Guidelines:**

- Take multiple photos of each person under different lighting
- Document lighting type in metadata
- Test model robustness across lighting conditions

### 5. Camera/Device Diversity

**Realistic diversity** (users capture on many devices):

| Device Category        | Coverage Target | Examples                                           |
| ---------------------- | --------------- | -------------------------------------------------- |
| Modern flagship phones | 30%             | iPhone 14+, Samsung S23+                           |
| Mid-range phones       | 25%             | iPhone 12-13, Samsung A-series                     |
| Budget phones          | 20%             | Older models, lower quality sensors                |
| Professional cameras   | 15%             | DSLR, mirrorless (backstory: dermatologist photos) |
| Webcams/cheap cameras  | 10%             | Lower resolution sources                           |

**Key differences:**

- Sensor quality affects color accuracy
- Resolution impacts detail visibility
- Compression algorithms vary
- HDR processing differs

**Action items:**

- Collect from multiple device types
- Document device metadata (phone model, camera settings)
- Test inference on various device outputs

### 6. Pose & Angle Diversity

**Realistic capture conditions:**

| Angle Category        | Coverage Target | Description         |
| --------------------- | --------------- | ------------------- |
| Front-facing (0°)     | 35%             | Straight-on photo   |
| Slight angle (15-30°) | 30%             | Common natural pose |
| Side view (45-90°)    | 20%             | Profile/side view   |
| Overhead angle        | 10%             | From above          |
| Downward angle        | 5%              | From below          |

**Challenges:**

- Shadows and foreshortening vary
- Lesions may not be visible from all angles
- Different regions visible in different poses

**Guidelines:**

- Multiple angles of same person when possible
- Natural poses preferred over forced angles
- Document camera angle in metadata

---

## Label Taxonomy

### 1. Skin Type Classification

**Classes**: 5 mutually-exclusive categories (based on sebum production and hydration)

```
normal (balanced)
├─ Description: Balanced sebum and hydration
├─ Characteristics: Clear, not excessively oily or dry
├─ Prevalence: ~20-30% of population
└─ Visual markers: Even texture, natural glow, no excessive shine

dry (dehydrated/lipid-deficient)
├─ Description: Insufficient natural oils
├─ Characteristics: Tight, flaky, prone to irritation
├─ Prevalence: ~20-30% of population
├─ Visual markers: Visible flaking, dull appearance, rough texture
└─ Challenges: Can look similar to combination in some areas

oily (excess sebum)
├─ Description: Excess sebum production
├─ Characteristics: Glossy, prone to acne and enlarged pores
├─ Prevalence: ~20-30% of population
├─ Visual markers: Visible shine, enlarged pores, acne-prone
└─ Challenges: Lighting affects appearance significantly

combination (mixed)
├─ Description: Multiple skin types in different facial zones
├─ Characteristics: T-zone (forehead, nose, chin) oily; cheeks normal/dry
├─ Prevalence: ~20-30% of population
├─ Visual markers: Shine in T-zone only, differential texture
└─ Challenges: Most common, requires careful observation of zones

sensitive (reactive)
├─ Description: Easily irritated, reactive to products/environment
├─ Characteristics: Redness, reactivity, reactive to temperature changes
├─ Prevalence: ~15-25% of population
├─ Visual markers: Redness, visible blood vessels, reactive areas
└─ Challenges: May overlap with other types, context-dependent
```

**Important notes:**

- Classes are **mutually exclusive** (choose exactly one)
- Based on sebum/hydration, not conditions
- Can have sensitive skin + oily/dry skin
- Document confidence if uncertain (see labeling instructions)

### 2. Hair Type Classification

**Classes**: 4 main categories (Andre Walker system, modified)

```
straight (Type 1)
├─ Description: Hair lies flat, no curl pattern
├─ Characteristics: Cuticles lie flat, minimal volume
├─ Curl pattern: 0° (no curl)
├─ Prevalence: ~15-20% of population
├─ Challenges: May have slight wave at ends
└─ Sub-types: Fine straight, medium straight, coarse straight

wavy (Type 2)
├─ Description: Loose waves, S-pattern
├─ Characteristics: Some volume, tousled appearance
├─ Curl pattern: 20-45° (loose wave)
├─ Prevalence: ~30-35% of population
├─ Challenges: Varies with moisture and styling
└─ Sub-types: Barely wavy, medium wavy, very wavy

curly (Type 3)
├─ Description: Spiral curls, bouncy
├─ Characteristics: Volume, defined curl pattern
├─ Curl pattern: 45-90° (spiral curl)
├─ Prevalence: ~20-25% of population
├─ Challenges: Curl pattern changes with weather, products
└─ Sub-types: Loose curls, medium curls, tight curls

coily (Type 4)
├─ Description: Tightly coiled, textured
├─ Characteristics: Densely packed coils, textured appearance
├─ Curl pattern: 90°+ (tight coil/coily)
├─ Prevalence: ~20-25% of population
├─ Challenges: Variation in coil tightness, prone to shrinkage
└─ Sub-types: Loose coils, medium coils, tight coils/kinky
```

**Important considerations:**

- Hair type can vary on individual head (document most prevalent)
- Styling products affect appearance
- Moisture/humidity causes variation
- Natural state preferred for accuracy
- Hair condition (damage, dryness) separate from type

### 3. Condition Classes (Detection/Severity)

**Categories**: 8 common skin & hair conditions with severity gradation

#### A. Acne

```
NORMAL (no acne)
├─ Description: No visible acne lesions
├─ Severity: 0
└─ Confidence: Easy to label

MILD_ACNE (scattered, comedonal)
├─ Description: 1-10 lesions total, mostly non-inflammatory
├─ Severity: 1
├─ Types: Blackheads, whiteheads, occasional papules
├─ Prevalence: Very common
├─ Labeling: Single box around clustered lesions OR individual boxes
└─ Challenge: Distinguish from other bumps

MODERATE_ACNE (10-40 papules/pustules)
├─ Description: Multiple inflammatory lesions scattered
├─ Severity: 2
├─ Types: Papules, pustules, some nodules
├─ Visual: 10-40 visible lesions across face
├─ Labeling: Box per lesion OR one box per cluster
└─ Consideration: May include scarring

SEVERE_ACNE (40+ lesions, cystic)
├─ Description: Extensive inflammatory acne, possible cysts
├─ Severity: 3
├─ Types: Nodules, cysts, significant inflammation
├─ Visual: 40+ lesions, possible scarring, extensive
├─ Labeling: Boxes around major affected areas
└─ Medical: May require dermatologist referral
```

**Labeling Strategy:**

- Option A: One bounding box per individual lesion (precise but time-consuming)
- Option B: One box per acne cluster (faster, less precise)
- Use confidence score if boundaries unclear

#### B. Blackheads/Comedones

```
Description: Open comedones with oxidized sebum
Severity: Usually mild (not separate classification)
Visual: Small dark dots, especially T-zone
Labeling: Too small to box individually, mark if extensive in patches
Ambiguity: Can be confused with dirt or pores—document in notes
Challenge: Resolution of phone cameras may not capture clearly
```

#### C. Rash/Dermatitis

```
MILD_RASH (localized, minimal inflammation)
├─ Description: Small area of redness, minimal scale
├─ Severity: 1
├─ Visual: Pink/red area, well-defined borders
└─ Labeling: One box encompassing entire rash area

MODERATE_RASH (10-30% face, some scaling)
├─ Description: Multiple areas or one large area
├─ Severity: 2
├─ Visual: Red, may have scale, defined areas
└─ Labeling: Box each area OR one encompassing box

SEVERE_RASH (>30% face, significant scale/inflammation)
├─ Description: Extensive area with significant inflammation
├─ Severity: 3
├─ Visual: Bright red, significant scaling, possible oozing
└─ Labeling: Encompassing box(es) around affected areas
```

**Differential diagnosis challenge:**

- Rash vs. Rosacea: Rosacea more persistent, on central face
- Rash vs. Sunburn: Sunburn more uniform, clear demarcation
- Rash vs. Irritant contact dermatitis: Contact usually localized to area of contact
- Document visual characteristics and suspected cause if known

#### D. Pigmentation Issues

```
HYPERPIGMENTATION (dark spots/patches)
├─ Description: Darker areas than surrounding skin
├─ Causes: Sun damage, melasma, post-inflammatory
├─ Severity: Usually cosmetic (1-3 scale for coverage)
├─ Labeling: Individual boxes around distinct spots/patches
└─ Note: Very common, varies significantly with sun exposure

HYPOPIGMENTATION (light spots/patches)
├─ Description: Lighter areas than surrounding skin
├─ Causes: Vitiligo, post-inflammatory, chemical damage
├─ Severity: Usually cosmetic (1-3 scale for coverage)
├─ Labeling: Individual boxes around distinct spots/patches
└─ Medical: Vitiligo warrants specialist referral
```

#### E. Eczema (Atopic Dermatitis)

```
MILD_ECZEMA (small patches, minimal inflammation)
├─ Description: Localized patches, subtle redness
├─ Severity: 1
├─ Visual: Pink patches, possibly with scale
└─ Labeling: Individual boxes around patches

MODERATE_ECZEMA (multiple patches, significant inflammation)
├─ Description: Multiple areas, notable inflammation and scale
├─ Severity: 2
├─ Visual: Red patches, visible scale, possible lichenification
└─ Labeling: Boxes around each patch or encompassing affected areas

SEVERE_ECZEMA (extensive areas, significant inflammation/scale)
├─ Description: Extensive inflammation, possible oozing
├─ Severity: 3
├─ Visual: Bright red, heavy scale, possible erosions
└─ Labeling: Encompassing boxes around affected areas
```

**Characteristics to note:**

- Usually symmetric and on typical locations (face, hands, flexural areas)
- History of itch/scratch important (may see excoriations)
- Chronic nature helps differentiate from acute rash

#### F. Infections (Fungal, Bacterial)

```
FUNGAL_INFECTION (candidosis, tinea, etc.)
├─ Description: Fungal growth, often with characteristic border
├─ Severity: 1-3 depending on extent
├─ Visual: Scale, erythema, possibly satellite lesions
├─ Labeling: Boxes around affected areas
└─ Challenge: Often indistinguishable from eczema without lab confirmation

BACTERIAL_INFECTION (cellulitis, impetigo, etc.)
├─ Description: Bacterial infection, inflammatory
├─ Severity: 2-3 (more concerning than fungal)
├─ Visual: Swelling, warmth, possibly pus, clear borders
├─ Labeling: Encompassing box around affected area
└─ Medical: Usually requires antibiotic treatment
```

**Labeling challenge:**

- Fungal vs. Eczema overlaps significantly visually
- Document suspected cause if known (athlete's foot pattern, etc.)
- May recommend lab confirmation in comments

#### G. Psoriasis

```
Description: Chronic inflammatory condition
Characteristics: Well-demarcated plaques, thick scale, symmetric
Visual: Red/violet patches with thick silvery scale
Severity: Usually 2-3 (chronic, may need specialist)
Labeling: Boxes around each plaque or encompassing plaques
Challenge: Can look like eczema—look for well-demarcated borders and thick scale
```

#### H. Hair Loss/Alopecia

```
NORMAL_HAIR (full density, no visible hair loss)
├─ Description: Healthy hair density
├─ Severity: 0
└─ Classification: Natural for age/genetics

MILD_HAIR_LOSS (visible thinning in specific areas)
├─ Description: 10-25% hair density reduction
├─ Severity: 1
├─ Types: Androgenetic alopecia (pattern), telogen effluvium (diffuse)
└─ Labeling: Mark affected areas (hairline recession, crown, etc.)

MODERATE_HAIR_LOSS (25-50% hair density reduction)
├─ Description: Noticeable thinning, visible scalp in some areas
├─ Severity: 2
├─ Types: Pattern baldness, significant telogen effluvium
└─ Labeling: Mark multiple affected areas

SEVERE_HAIR_LOSS (>50% hair density reduction)
├─ Description: Significant baldness, large areas of visible scalp
├─ Severity: 3
├─ Types: Advanced pattern baldness, significant alopecia areata
└─ Labeling: Mark all affected areas
```

**Important notes:**

- Natural variation with age (male pattern baldness common)
- Hairline position varies by genetics
- Telogen effluvium (temporary) vs. androgenetic alopecia (permanent)
- Document suspected cause if known

#### I. Other Conditions

**Document any additional conditions observed:**

- Moles/nevi (benign, but may warrant dermatologist referral if changing)
- Birthmarks/port-wine stains
- Scars/scarring
- Warts
- Milia
- Sebaceous hyperplasia
- Other anomalies

---

## Labeling Instructions

### General Principles

1. **One condition per box** - Each bounding box should contain one lesion type
2. **Tightness** - Boxes should be snug around lesion, not loose
3. **Consistency** - Same person labeling whole dataset maintains consistency
4. **Ambiguity** - When unsure, document in notes and possibly skip
5. **Consensus** - Complex cases reviewed by 2+ labelers

### Step-by-Step Labeling Process

#### Phase 1: Pre-Labeling Preparation

```
1. Load image in labeling tool (CVAT recommended)
2. Check metadata:
   - Device type captured
   - Lighting conditions
   - Image quality/sharpness
   - Any special circumstances
3. Document image-level metadata:
   - Age range (if known): 13-18, 19-25, 26-35, etc.
   - Fitzpatrick skin tone: I, II, III, IV, V, VI
   - Reported gender: M/F/NB/Prefer not to say
   - Reported skin type: normal/dry/oily/combination/sensitive
   - Reported hair type: straight/wavy/curly/coily
   - Lighting: natural_daylight/window/incandescent/LED/flash
   - Camera: [specific device if known]
   - Image quality: excellent/good/acceptable/poor
```

#### Phase 2: Skin Type Classification

**Instructions:**

1. Examine entire face for sebum production and hydration
2. Pay special attention to:
   - **T-zone** (forehead, nose, chin)
   - **Cheeks and temples**
   - **Overall texture and appearance**
3. Read characteristics in taxonomy above
4. Select best match (must choose exactly one)

**Decision tree:**

```
Is the skin shiny/glossy with visible sebum?
├─ YES
│  └─ Is shinier in T-zone only?
│     ├─ YES → Combination
│     └─ NO (full face shiny) → Oily
└─ NO (not shiny)
   └─ Is the skin flaky/dry/tight-looking?
      ├─ YES → Dry
      └─ NO
         └─ Is the skin reactive/red/sensitive-looking?
            ├─ YES → Sensitive
            └─ NO → Normal
```

**Confidence levels:**

- Mark confidence: High / Medium / Low
- Low confidence if: Lighting unclear, makeup present, multiple indicators

#### Phase 3: Hair Type Classification

**Instructions:**

1. Examine visible hair for curl pattern
2. Focus on hair in foreground/sides of face
3. If mixed types on head, document most prevalent
4. Read characteristics in taxonomy above
5. Select best match (must choose exactly one)

**Decision tree:**

```
Does the hair have any visible curl/wave pattern?
├─ NO (lies flat, straight) → Straight
└─ YES (has curl/wave)
   └─ How tight is the pattern?
      ├─ Loose waves (S-shaped) → Wavy
      ├─ Defined spirals/coils (45-90°) → Curly
      └─ Very tight coils (90°+) → Coily
```

**Confidence levels:**

- Mark confidence: High / Medium / Low
- Low confidence if: Styled/wet, extensions, unclear angle

#### Phase 4: Condition Detection (Bounding Box Labeling)

**Step 1: Identify regions of concern**

Scan image systematically:

- Central face (forehead, nose, cheeks)
- Chin and jawline
- Around eyes
- Neck/décolletage (if visible)
- Ears (if visible)
- Scalp/hairline (if visible)

**Step 2: For each lesion/area, create bounding box**

```
For ACNE/COMEDONES:
  └─ Draw box around each lesion if >2mm visible
  └─ For clusters: Either individual boxes OR one encompassing box
  └─ Set confidence based on clarity (High=clear, Medium=subtle, Low=uncertain)

For RASH/DERMATITIS:
  └─ Draw encompassing box around continuous rash area
  └─ Multiple boxes if multiple distinct areas
  └─ Ensure box captures all affected area with ~5mm margin

For PIGMENTATION:
  └─ Draw box around distinct spots/patches
  └─ Don't include surrounding normal skin
  └─ Multiple boxes for multiple spots

For INFECTIONS/ECZEMA/PSORIASIS:
  └─ Draw box around affected area(s)
  └─ Include scale/inflammation but not surrounding normal skin
  └─ Multiple boxes for multiple distinct patches

For HAIR LOSS:
  └─ If localized: Box around affected area (e.g., hairline recession)
  └─ If diffuse: Mark overall appearance with notation
  └─ Document area percentage affected
```

**Step 3: Assign severity level**

For each condition box, assign severity (0-3):

```
Severity 0: None/Normal (no box drawn)
Severity 1: Mild (few lesions, minimal inflammation, localized)
Severity 2: Moderate (multiple lesions, moderate inflammation, broader area)
Severity 3: Severe (extensive lesions, significant inflammation, large area)
```

**Step 4: Document ambiguities and notes**

For each box, optionally add notes:

```
Examples:
- "Unclear if acne or other bump—probable comedone"
- "Could be eczema or allergic rash—recommend dermatologist"
- "Fungal infection suspected—lab confirmation recommended"
- "Post-inflammatory hyperpigmentation, likely from previous acne"
- "Lighting makes severity difficult to assess—verify in person"
```

### Tool-Specific Instructions

#### For CVAT (Computer Vision Annotation Tool)

```python
# CVAT Project Setup
1. Create project: "Haski_Skin_Hair_2025"
2. Upload images: Dataset folder with metadata CSV
3. Create two tasks:
   Task A: "Classification" (skin type + hair type)
   Task B: "Detection" (lesion bounding boxes + severity)

# Classification Task (CVAT)
Labels: [
  "normal", "dry", "oily", "combination", "sensitive",
  "straight", "wavy", "curly", "coily"
]
Attributes:
  - confidence: High / Medium / Low
  - skin_type_noted: [text field]

# Detection Task (CVAT)
Labels: [
  "acne_mild", "acne_moderate", "acne_severe",
  "rash_mild", "rash_moderate", "rash_severe",
  "eczema_mild", "eczema_moderate", "eczema_severe",
  "infection_fungal", "infection_bacterial",
  "psoriasis", "hyperpigmentation", "hypopigmentation",
  "hair_loss_mild", "hair_loss_moderate", "hair_loss_severe"
]
Attributes:
  - confidence: High / Medium / Low
  - notes: [text field, optional]
```

#### For LabelImg (Simple Bounding Box)

```
1. Configure classes in data/predefined_classes.txt
2. For each image:
   - Load in LabelImg
   - Draw boxes around lesions
   - Select appropriate class from dropdown
   - Save as .xml (Pascal VOC format)

# Class list for LabelImg:
acne
rash
dermatitis
eczema
infection_fungal
infection_bacterial
psoriasis
hyperpigmentation
hypopigmentation
hair_loss
```

#### For Roboflow (Recommended for small teams)

```
1. Create project at roboflow.com
2. Upload images + metadata CSV
3. Use web interface to:
   - Annotate bounding boxes
   - Assign classes
   - Track completion percentage
   - Generate augmented dataset
4. Export when complete in multiple formats:
   - YOLO format (for detection model)
   - Pascal VOC (for TensorFlow)
   - COCO JSON (for evaluation)
```

### Quality Control During Labeling

**Before finalizing each image:**

1. **Completeness check**

   - [ ] Skin type selected
   - [ ] Hair type selected
   - [ ] All visible conditions marked
   - [ ] No areas obviously missed

2. **Accuracy check**

   - [ ] Boxes tightly fit lesions (not loose)
   - [ ] Severity levels appropriate
   - [ ] No mislabeled classes
   - [ ] Confidence levels reasonable

3. **Metadata check**

   - [ ] Age range documented
   - [ ] Fitzpatrick tone documented
   - [ ] Gender preference recorded
   - [ ] Lighting conditions noted
   - [ ] Device information captured

4. **Special cases**
   - [ ] Any ambiguous regions noted
   - [ ] Unusual presentations documented
   - [ ] Medical concerns flagged for review

### Handling Ambiguous Cases

**When unsure about a label:**

```
Option A: Review with team
  - Flag for secondary review
  - Different annotator provides opinion
  - Consensus established

Option B: Expert consultation
  - Dermatologist reviews if available
  - Medical literature consulted
  - Final determination made

Option C: Skip and document
  - Mark image as "under-review"
  - Include in future review batch
  - May exclude from initial training

Common ambiguities:
1. Acne vs. other bumps (keratosis, milia, etc.)
   → Look for comedone center, inflammation patterns

2. Eczema vs. Rash vs. Contact Dermatitis
   → Borders, scale, symmetric distribution

3. Fungal vs. other infections
   → Look for satellite lesions, borders, scale type

4. Rosacea vs. Rash
   → Rosacea usually central face, persistent

5. Melasma vs. other hyperpigmentation
   → Melasma symmetric, on cheeks/forehead
```

---

## Privacy & Consent Framework

### 1. Consent Requirements

**Explicit Consent Language:**

```
Before including any image in training dataset, obtain written consent:

"I consent to my photo(s) being used for machine learning model
development for skin and hair analysis. I understand that:

□ My photo will be used to train AI models for Haski
□ My photo may be shared with research partners [if applicable]
□ My photo will be stored securely with restricted access
□ My photo will NOT be used for facial recognition
□ My photo will be anonymized and de-identified
□ I can request deletion of my image(s) at any time
□ No commercial use without separate compensation agreement
□ Deletion may not be possible after model training completion
   (but new models won't be retrained with my data)
□ I acknowledge the risks:
   - Model may have errors
   - Model may exhibit biases
   - Model may perform differently on my skin tone/type
   - Alternative models/tools exist

Consent given for: □ Research only | □ Commercial use | □ Both
Opt-in for data sale: □ Yes, compensate me | □ No"

Signature: ________________  Date: ________________
```

**Important points:**

- EXPLICIT consent required (not opt-out)
- Options to limit use (research vs. commercial)
- Clear statement of risks
- Acknowledgment of potential limitations
- Right to deletion/withdrawal

### 2. Metadata Collection & Privacy

**What to collect:**

```
User-reported demographics:
├─ Age range (not exact age): "19-25", "26-35", etc.
├─ Gender identity: "Male", "Female", "Non-binary", "Prefer not to say"
├─ Fitzpatrick skin tone: I, II, III, IV, V, VI
├─ Location/ethnicity (optional): "South Asian", "African American", etc.
└─ Medical history (if relevant): "Known eczema", "Diabetic", etc.

Image metadata:
├─ Lighting: "natural_daylight", "window", "incandescent", "LED", "flash"
├─ Device: "iPhone 14", "Samsung S23", "DSLR", etc.
├─ Time of day: "morning", "afternoon", "evening"
├─ Skincare routine note: "Just applied moisturizer", "Makeup on", etc.
├─ Recent treatments: "Accutane treatment", "Dermatologist visit", etc.
└─ Environmental factors: "High humidity", "Cold weather", etc.

Consent metadata:
├─ Consent date
├─ Consent type: "research_only" / "commercial" / "both"
├─ Data sale opt-in: "yes" / "no"
├─ Deletion request date (if applicable)
└─ Contact email (for deletion requests)
```

**What NOT to collect:**

```
❌ Exact date of birth (use age range instead)
❌ Full name or identifying information
❌ Medical ID numbers
❌ Insurance information
❌ Exact location (use region/state level)
❌ Facial identifying features unrelated to skin/hair
❌ Other personally identifying information
```

### 3. Data Security & Access Control

**Storage requirements:**

```
Raw images storage:
├─ Encrypted at rest (AES-256)
├─ Encrypted in transit (TLS 1.2+)
├─ Access restricted to Haski team
├─ Backed up to secure location
├─ Deletion log maintained
└─ Retention policy: Until user requests deletion OR 2 years max

Metadata storage:
├─ Separate from images
├─ Pseudonymous ID linking (UUID, not name)
├─ Encrypted database
├─ Access via password + 2FA
└─ Regular access audits

Trained models:
├─ Only aggregate statistics retained
├─ No individual images embedded
├─ Model weights public (GitHub)
└─ Model training data documented but not released
```

**Access control:**

```
Data access levels:

Public (Model + aggregate stats):
└─ Published to GitHub, Hugging Face
└─ Anyone can download trained models
└─ No individual images or raw data

Team (Training + evaluation):
└─ ML engineers, data scientists
└─ Raw images + metadata
└─ Subject to signed data agreement
└─ 2FA required

Management (Deletion requests):
└─ Privacy officer, legal team
└─ Access logs for deletion compliance
└─ Right to audit data

Deleted (User request):
└─ User UUID pseudonymized
└─ All associated images purged
└─ Metadata retained for compliance (count, date, reason)
```

### 4. Deletion Request Process

**User-initiated deletion:**

```
1. User sends email: "data-deletion@haski.com"
2. Include: User ID / Email / Phone
3. System identifies matching user UUID
4. All raw images deleted from storage
5. Metadata entry updated: "deleted_date": "2025-10-24"
6. Confirmation email sent within 7 days
7. New models NOT retrained on deleted data
8. Previous models remain published (data already in model weights)

Note: Deletion from training data takes effect for NEXT model
version, not retroactively for existing published models.
```

### 5. Data Sale & Compensation (Optional)

**For commercial use agreement:**

```
If collecting data for potential data sale/licensing:

Data sale agreement:
├─ Individual contributor compensation: $X per image
├─ Demographic bonus: +$X for underrepresented groups
├─ Exclusive use period: None / 6 months / 1 year
├─ Continued compensation: One-time / Royalty-based
└─ Right of first refusal for licensees

Example rates:
- Base: $1-5 per high-quality image
- Underrepresented demographic (rare skin tone): +$5
- High-quality (professional photo): +$2
- Total potential: $3-12 per image

Payment via:
├─ Direct bank transfer
├─ PayPal
├─ Crypto (if desired)
└─ Store credit option
```

---

## Recommended Tools

### 1. CVAT (Computer Vision Annotation Tool)

**Best for: Professional teams, complex tasks, collaborative workflow**

```
✅ Pros:
- Open source (free, self-hosted option)
- Excellent collaborative features
- Version control for annotations
- Multiple annotation types (boxes, polygons, masks)
- Dataset management built-in
- Quality assurance tools (inter-rater agreement, review workflow)
- Export multiple formats (YOLO, COCO, etc.)

❌ Cons:
- Steeper learning curve
- Requires server infrastructure
- More complex setup

📍 Typical workflow:
1. Server setup: docker-compose up
2. Create project, upload images
3. Assign annotators to tasks
4. Annotators label in web interface
5. QA reviewer checks work
6. Export dataset in desired format

💾 URL: https://github.com/cvat-ai/cvat
```

**Setup example:**

```bash
# Option 1: Docker (recommended)
git clone https://github.com/cvat-ai/cvat
cd cvat
docker-compose up -d
# Access at: http://localhost:8080

# Option 2: Local installation
pip install cvat-sdk
# Then use with local file backend
```

### 2. LabelImg

**Best for: Simple bounding box tasks, small datasets, quick start**

```
✅ Pros:
- Very easy to learn (intuitive GUI)
- No server required
- Fast labeling
- Exports to multiple formats
- Good for simple box detection

❌ Cons:
- Limited to bounding boxes (no polygons/masks)
- No collaborative features
- No built-in QA
- Manual image management

📍 Typical workflow:
1. Install LabelImg
2. Open image directory
3. Draw boxes, select class
4. Save XML files alongside images
5. Convert to desired format

💾 URL: https://github.com/heartexlabs/labelImg
```

**Setup:**

```bash
# Installation
pip install labelimg

# Run
labelimg

# Configure classes in data/predefined_classes.txt:
# acne
# rash
# eczema
# etc.
```

### 3. Roboflow

**Best for: Small to mid-sized teams, need data augmentation, cloud-based collaboration**

```
✅ Pros:
- Web-based (no local install)
- Built-in data augmentation
- Automatic format conversion
- Version management
- Free tier available
- Integration with training pipelines
- Mobile-friendly annotation

❌ Cons:
- Paid for larger datasets
- Cloud-dependent
- Less customizable than CVAT
- Third-party service (data privacy considerations)

📍 Typical workflow:
1. Create account at roboflow.com
2. Create project
3. Upload images
4. Annotate in web interface
5. Roboflow generates augmented dataset
6. Export in any format needed

💾 Cost: Free tier (1000 images), then $12-50+/month
💾 URL: https://roboflow.com
```

**Example workflow:**

```python
# After annotating in Roboflow, export and use:

from roboflow import Roboflow

rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace().project("haski-skin-hair")
dataset = project.versions(1).download("yolov8")

# Now train with:
# yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=100
```

### 4. Prodigy

**Best for: Active learning, iterative labeling, high-efficiency needed**

```
✅ Pros:
- Very efficient UI (keyboard shortcuts, smart suggestions)
- Active learning mode (prioritizes uncertain cases)
- Weak supervision tools
- Multi-user with streaming updates
- Export to standard formats

❌ Cons:
- Paid tool ($490 one-time license)
- Less free tier than competitors
- Smaller ecosystem

📍 Best for:
- Large-scale labeling projects
- Need high efficiency
- Team size justifies cost

💾 URL: https://prodi.gy
💾 Cost: $490 one-time or $50-200/month depending on features
```

### 5. Label Studio

**Best for: Enterprise teams, complex pipelines, on-premise deployment**

```
✅ Pros:
- Open source option available
- Enterprise version with advanced features
- Flexible setup (cloud, on-prem, hybrid)
- Multiple task types
- API-first design
- Integration with ML workflows

❌ Cons:
- More complex setup
- Enterprise features paid
- Steeper learning curve

📍 URL: https://labelstud.io
💾 Cost: Open source (free) or Enterprise ($15-100+/month)
```

### Tool Comparison Table

| Tool             | Cost      | Setup     | Collaboration | Ease       | Export     | Best For    |
| ---------------- | --------- | --------- | ------------- | ---------- | ---------- | ----------- |
| **CVAT**         | Free      | Complex   | ⭐⭐⭐⭐⭐    | Medium     | ⭐⭐⭐⭐⭐ | Pro teams   |
| **LabelImg**     | Free      | Easy      | ❌            | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | Quick start |
| **Roboflow**     | Free/Paid | Very Easy | ⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Teams + aug |
| **Prodigy**      | Paid      | Medium    | ⭐⭐⭐        | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | High-scale  |
| **Label Studio** | Free/Paid | Medium    | ⭐⭐⭐⭐      | ⭐⭐⭐     | ⭐⭐⭐⭐   | Enterprise  |

**Recommended path for Haski:**

```
Phase 1 (100 images, team learning): LabelImg
├─ Fast onboarding
├─ Simple workflow
└─ Low cost

Phase 2 (500-2000 images, small team): Roboflow
├─ Collaboration
├─ Augmentation included
├─ Affordable
└─ Good QA tools

Phase 3 (2000+ images, large scale): CVAT + Roboflow
├─ CVAT for primary annotation
├─ QA reviews
├─ Roboflow for augmentation/export
└─ Best of both worlds
```

---

## Quality Assurance

### 1. Inter-Rater Reliability (IRR)

**Ensure consistency between annotators:**

```
Setup:
1. Select 50 random images (diverse in conditions/demographics)
2. Have 2+ independent annotators label same images
3. Compare results using metrics below

Metrics:

For classification (skin type, hair type):
├─ Cohen's Kappa: Measures agreement beyond chance
│  ├─ 0.81-1.00: Excellent agreement ✅
│  ├─ 0.61-0.80: Substantial agreement ⚠️
│  ├─ 0.41-0.60: Moderate agreement ❌
│  └─ <0.40: Poor agreement ❌ (retrain annotators)
└─ Percentage agreement: Simple % of matching labels

For detection (bounding boxes):
├─ IoU (Intersection over Union): Overlap of boxes
│  ├─ >0.75: Excellent ✅
│  ├─ 0.50-0.75: Good ⚠️
│  ├─ 0.25-0.50: Poor ❌
│  └─ <0.25: Unacceptable ❌
└─ F1 score: Both precision and recall
   ├─ >0.85: Excellent ✅
   └─ <0.70: Retrain annotators ❌
```

**Python calculation example:**

```python
from sklearn.metrics import cohen_kappa_score, f1_score

# For classification
annotator1_labels = ["normal", "dry", "oily", ...]
annotator2_labels = ["normal", "dry", "combination", ...]

kappa = cohen_kappa_score(annotator1_labels, annotator2_labels)
agreement = (annotator1 == annotator2).mean()

print(f"Cohen's Kappa: {kappa:.3f}")
print(f"Agreement: {agreement:.1%}")

# For detection (if using IoU)
def calculate_iou(box1, box2):
    """Calculate IoU between two boxes"""
    x_min = max(box1[0], box2[0])
    y_min = max(box1[1], box2[1])
    x_max = min(box1[2], box2[2])
    y_max = min(box1[3], box2[3])

    if x_max < x_min or y_max < y_min:
        return 0

    intersection = (x_max - x_min) * (y_max - y_min)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection

    return intersection / union

# Compare boxes from two annotators
ious = [calculate_iou(b1, b2) for b1, b2 in zip(boxes1, boxes2)]
print(f"Mean IoU: {np.mean(ious):.3f}")
```

### 2. Label Distribution Checks

**Ensure balanced dataset:**

```python
import pandas as pd

# Load labels
df = pd.read_csv("annotations.csv")

# Check skin type distribution
print(df['skin_type'].value_counts())
# Expected: roughly 20% each for 5 classes

# Check demographics
print(df['skin_tone_fitzpatrick'].value_counts())
# Expected: roughly 15% for Types I-VI (equal distribution)

print(df['age_range'].value_counts())
# Expected: Even distribution across age ranges

# Check condition prevalence
print(df['has_acne'].value_counts())
# Expected: Some imbalance is OK (not all have acne)
# But avoid highly skewed (e.g., 95% normal, 5% abnormal)
```

**Target distributions:**

```
Skin Types (balanced):
- normal: 20% (1000 images)
- dry: 20% (1000 images)
- oily: 20% (1000 images)
- combination: 20% (1000 images)
- sensitive: 20% (1000 images)

Fitzpatrick Skin Tones (balanced):
- I: 15% (750 images)
- II: 15% (750 images)
- III: 20% (1000 images)
- IV: 20% (1000 images)
- V: 15% (750 images)
- VI: 15% (750 images)

Conditions (may be imbalanced—OK):
- Normal (no conditions): 60-70%
- Mild acne: 15-20%
- Moderate acne: 5-10%
- Other conditions: 5-10%
```

### 3. Visual Quality Checks

**Automated checks:**

```python
import cv2
import numpy as np
from PIL import Image

def check_image_quality(image_path):
    """Automated quality checks"""
    img = cv2.imread(image_path)

    checks = {
        "size": img.shape,  # Should be reasonable
        "resolution": img.shape[0] * img.shape[1],  # Pixels
        "sharpness": cv2.Laplacian(img, cv2.CV_64F).var(),  # Blurriness
        "brightness": np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:,:,2]),
        "contrast": cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:,:,2].std()
    }

    issues = []
    if checks["resolution"] < 640*480:
        issues.append("LOW_RESOLUTION")
    if checks["sharpness"] < 100:
        issues.append("BLURRY")
    if checks["brightness"] < 20 or checks["brightness"] > 235:
        issues.append("EXPOSURE_ISSUE")
    if checks["contrast"] < 30:
        issues.append("LOW_CONTRAST")

    return checks, issues

# Scan all images
for img_file in images_dir.glob("*.jpg"):
    checks, issues = check_image_quality(img_file)
    if issues:
        print(f"{img_file}: {issues}")
```

**Manual review criteria:**

```
For each image, verify:

✅ Image clarity
   - Not blurry
   - Not obscured
   - Face visible and well-lit

✅ Face visibility
   - Sufficient facial area visible
   - At least 50% of face in frame (for classification)
   - Region of interest (skin/hair condition) clearly visible

✅ No artifacts
   - No heavy makeup masking skin
   - No extreme filters applied
   - No obvious photoshop
   - No identifying marks visible

✅ Image integrity
   - Image not corrupted
   - File format standard (JPG/PNG)
   - Metadata readable
   - Dimensions reasonable (480p minimum)

❌ Reject if:
   - Too low resolution (<480p)
   - Extreme lighting/shadow
   - Face not visible
   - Obvious medical dressing
   - Copyright/watermark concerns
```

### 4. Medical Accuracy Review

**For serious/atypical cases:**

```
Flag for expert review:

1. Suspected serious conditions:
   - Possible cellulitis (swelling, warmth, fever indicators)
   - Possible skin cancer (changing mole, irregular borders)
   - Possible severe burn
   - Any image suggesting medical emergency

2. Complex cases:
   - Multiple conditions present
   - Ambiguous differential diagnosis
   - Unusual presentation
   - Potential drug-induced condition

3. Documentation needed:
   - Expert opinion: Dermatologist review
   - Final label approved by: [Name], [Date]
   - Notes: [Expert observations]
   - Confidence: High / Medium / Low
```

---

## Data Management

### 1. Dataset Organization

**Recommended directory structure:**

```
ml/data/
├── raw/
│   ├── images/
│   │   ├── img_001.jpg
│   │   ├── img_002.jpg
│   │   └── ... (all raw images)
│   ├── metadata/
│   │   ├── image_metadata.csv
│   │   ├── consent_log.csv
│   │   └── data_dictionary.md
│   └── annotations/
│       ├── labels_classification.csv
│       ├── labels_detection.json (COCO format)
│       └── labels_detection_yolo/ (*.txt files)
│
├── processed/
│   ├── train/
│   │   ├── images/
│   │   ├── labels/
│   │   └── metadata.csv
│   ├── val/
│   │   ├── images/
│   │   ├── labels/
│   │   └── metadata.csv
│   ├── test/
│   │   ├── images/
│   │   ├── labels/
│   │   └── metadata.csv
│   └── splits.json (train/val/test assignments)
│
├── augmented/
│   ├── train_augmented/
│   │   ├── images/
│   │   ├── labels/
│   │   └── augmentation_log.csv
│   └── augmentation_config.yaml
│
├── exports/
│   ├── train_coco.json
│   ├── val_coco.json
│   ├── train.txt (YOLO format)
│   ├── val.txt
│   ├── data.yaml (YOLO config)
│   └── class_mapping.json
│
└── logs/
    ├── data_collection_log.txt
    ├── annotation_progress.csv
    ├── quality_assurance_report.txt
    ├── inter_rater_reliability.txt
    └── deletion_requests.log
```

### 2. Metadata CSV Format

**Main image metadata (metadata.csv):**

```csv
image_id,filename,image_uuid,consent_given,consent_date,consent_type,skin_type,skin_type_confidence,skin_tone_fitzpatrick,age_range,gender,hair_type,hair_type_confidence,lighting,camera_device,image_quality,has_acne,acne_severity,has_rash,has_eczema,has_hyperpigmentation,has_hair_loss,notes,annotator,annotation_date,qa_reviewer,qa_approval_date,qa_notes,deletion_requested,deletion_date
001,img_001.jpg,uuid-abc123,yes,2025-10-01,commercial,combination,high,IV,26-35,Female,wavy,high,natural_daylight,iPhone 14,excellent,true,2,false,false,false,false,Some comedones on chin area,john_doe,2025-10-02,jane_smith,2025-10-03,Approved,no,NULL
002,img_002.jpg,uuid-def456,yes,2025-10-01,research_only,normal,high,II,19-25,Male,straight,high,window,Samsung S23,good,false,0,false,false,false,true,Mild hairline recession—normal age variation,john_doe,2025-10-02,jane_smith,2025-10-03,Approved,no,NULL
...
```

**Consent log (consent_log.csv):**

```csv
user_id,email,image_ids,consent_date,consent_expiry,consent_type,data_sale_opt_in,special_notes,deletion_requested,deletion_date,deletion_processed
user_123,john@example.com,"[001,002,003]",2025-10-01,NULL,commercial,yes,Known eczema patient,no,NULL,NULL
user_456,jane@example.com,"[004,005]",2025-10-02,NULL,research_only,no,Has psoriasis history,yes,2025-10-15,2025-10-16
...
```

### 3. Data Version Control

**Track dataset versions:**

```yaml
# datasets/versions.yaml
dataset_version: v2.1
date_created: 2025-10-24
description: "Balanced skin tone dataset with 5K images"

statistics:
  total_images: 5000
  train_images: 3500 (70%)
  val_images: 750 (15%)
  test_images: 750 (15%)

demographics:
  skin_tones:
    type_1: 750 (15%)
    type_2: 750 (15%)
    type_3: 1000 (20%)
    type_4: 1000 (20%)
    type_5: 750 (15%)
    type_6: 750 (15%)
  age_groups:
    "13-18": 500 (10%)
    "19-25": 750 (15%)
    "26-35": 1250 (25%)
    "36-45": 1000 (20%)
    "46-55": 750 (15%)
    "56-65": 500 (10%)
    "65+": 250 (5%)

labels:
  skin_types:
    normal: 1000 (20%)
    dry: 1000 (20%)
    oily: 1000 (20%)
    combination: 1000 (20%)
    sensitive: 1000 (20%)
  conditions:
    no_condition: 3000 (60%)
    mild_acne: 1000 (20%)
    rash_dermatitis: 600 (12%)
    other: 400 (8%)

annotations_complete: 100%
qa_approved: 98%
quality_score: 0.94

changes_from_v2.0:
  - Added 1000 new images with better skin tone diversity
  - Removed 50 poor quality images
  - Re-annotated 200 ambiguous images
  - Inter-rater kappa improved from 0.82 to 0.87

next_steps:
  - Collect 1000 more Type I images (underrepresented)
  - Expand hair loss dataset
  - Add more severe condition examples
```

### 4. Annotation Progress Tracking

**Monitor team progress:**

```python
# annotation_progress_tracking.py
import pandas as pd
from datetime import datetime

# Track annotator productivity
progress_df = pd.DataFrame({
    'annotator': ['john_doe', 'jane_smith', 'bob_wilson'],
    'images_annotated': [850, 920, 640],
    'images_qa_approved': [820, 910, 630],
    'avg_annotation_time_min': [8.5, 7.2, 9.1],
    'kappa_score': [0.86, 0.89, 0.82],
    'notes': ['Fast, consistent', 'Excellent quality', 'Needs retraining on detection']
})

# Calculate project progress
total_images = 5000
annotated = progress_df['images_qa_approved'].sum()
completion_rate = annotated / total_images * 100

print(f"""
ANNOTATION PROGRESS REPORT
==========================
Date: {datetime.now().strftime('%Y-%m-%d')}

Overall Progress: {completion_rate:.1f}% ({annotated}/{total_images})
Estimated completion: {estimated_date}

Per-Annotator Stats:
{progress_df.to_string(index=False)}

Bottlenecks:
- QA approval rate: {qa_approval_rate:.1%}
- Average annotation time: {avg_time:.1f} min/image
- Est. time to 100%: {est_hours} hours

Actions needed:
- Consider adding annotators (currently at {completion_rate:.1f}%)
- Retrain low-performing annotators (kappa < 0.85)
- Review challenging images with team
""")
```

---

## Checklist for Data Collection

**Pre-collection:**

```
☐ Obtain IRB approval (if research institution)
☐ Create privacy policy & data sharing agreements
☐ Design consent form
☐ Set up secure storage infrastructure
☐ Recruit diverse annotators (represent user demographics)
☐ Train annotators on taxonomy & tools
☐ Test annotation workflow on pilot dataset (50 images)
☐ Calculate inter-rater reliability on test set
```

**During collection:**

```
☐ Collect across all demographic groups
☐ Document metadata for every image
☐ Obtain explicit consent before including image
☐ Perform quality checks on received images
☐ Track annotation progress weekly
☐ Monitor inter-rater agreement
☐ Flag ambiguous/complex cases for expert review
☐ Maintain deletion request log
```

**Before training:**

```
☐ Finalize all annotations
☐ QA review 100% of images
☐ Verify demographic balance
☐ Check IRR metrics (Kappa > 0.80)
☐ Generate dataset report with statistics
☐ Create version record (versions.yaml)
☐ Backup raw dataset securely
☐ Generate train/val/test splits
☐ Document any exclusions/deletions
☐ Export to training formats (YOLO, COCO, etc.)
```

---

## Summary

This guide provides a framework for collecting high-quality, diverse, and ethically-sound training data for skin and hair analysis models. Key takeaways:

1. **Diversity is critical**: Ensure representation across skin tones, ages, genders, lighting, and devices
2. **Clear taxonomy**: Define classes precisely to minimize ambiguity
3. **Privacy first**: Explicit consent, secure storage, respect deletion rights
4. **Quality assurance**: IRR metrics, expert review, automated checks
5. **Tool selection**: Choose based on team size and needs (LabelImg → Roboflow → CVAT)
6. **Documentation**: Track everything—metadata, annotations, versions, deletions

**Next steps:**

1. Finalize consent forms and privacy policy
2. Select annotation tool
3. Recruit and train annotators
4. Collect pilot dataset (100 images)
5. Measure IRR and iterate
6. Scale to full dataset (5000+ images)

---

**Last Updated**: 2025-10-24  
**Version**: 1.0  
**Author**: Haski ML Team
