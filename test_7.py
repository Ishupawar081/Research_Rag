import re

def parse_metadata(raw_texts):
    # Regexes
    _EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
    _GROUPED_EMAIL_RE = re.compile(r"\{([^}]+)\}\s*@\s*([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")
    
    # Strip from names
    _AUTHOR_STRIP_RE = re.compile(
        r"[\*∗†‡§¶#]"
        r"|\b\d+(?:,\d+)*\b"
        r"|\bemail\b"
        r"|\bcorresponding\b"
        r"|[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]",
        re.IGNORECASE,
    )
    
    blacklist = {
        'university', 'institute', 'department', 'lab', 'laboratory',
        'college', 'school', 'center', 'centre', 'research', 'technology',
        'faculty', 'academy', 'group', 'corporation', 'inc', 'ltd',
        'ai', 'labs', 'google', 'sony', 'hospital', 'clinic', 'company',
        'gmbh', 'llc', 'sciences', 'engineering', 'dept', 'univ', 'inst',
        'national', 'international'
    }

    # 1. Combine multi-column layouts. We'll join all raw texts with a newline
    combined = "\n".join(raw_texts)
    
    # 2. Extract and expand emails
    emails = []
    # Find grouped emails first
    for match in _GROUPED_EMAIL_RE.finditer(combined):
        users_str, domain = match.groups()
        for user in users_str.split(','):
            user = user.strip()
            if user:
                emails.append(f"{user}@{domain}")
    # Remove grouped emails from text
    combined = _GROUPED_EMAIL_RE.sub("", combined)
    
    # Find standard emails
    for match in _EMAIL_RE.finditer(combined):
        emails.append(match.group(0))
    combined = _EMAIL_RE.sub("", combined)
    
    # deduplicate emails
    seen_emails = set()
    deduped_emails = []
    for e in emails:
        if e not in seen_emails:
            seen_emails.add(e)
            deduped_emails.append(e)

    # 3. Classify remaining text
    extracted_authors = []
    extracted_affiliations = []
    
    lines = []
    for line in combined.split('\n'):
        # also split on commas and 'and' if it looks like a list
        if ',' in line or ' and ' in line.lower():
            l = re.sub(r"\band\b", ",", line, flags=re.IGNORECASE)
            for part in l.split(','):
                if part.strip(): lines.append(part.strip())
        else:
            # Maybe split by Greek letters / numbers / asterisks followed by uppercase
            # E.g. "Hamish Ivison α Noah A. Smith" -> split by α
            # "Kumar Shridhar ∗ Alessandro" -> split by ∗
            # We can split on any sequence of markers that is followed by a space and an uppercase letter
            parts = re.split(r"(?:^|\s)[0-9,α-ωΑ-Ω*∗†‡§¶#]+\s+(?=[A-Z])", line)
            if len(parts) > 1:
                for part in parts:
                    if part.strip(): lines.append(part.strip())
            else:
                if line.strip(): lines.append(line.strip())

    for line in lines:
        if not line: continue
        
        # Check notes
        l_lower = line.lower()
        if 'equal contribution' in l_lower or 'corresponding author' in l_lower or 'supported by' in l_lower:
            continue
            
        # Check affiliation
        is_affil = any(m in l_lower for m in blacklist)
        if is_affil:
            # We should probably split affiliations too by markers
            extracted_affiliations.append(line)
            continue
            
        # Clean potential author
        clean_name = _AUTHOR_STRIP_RE.sub("", line)
        clean_name = re.sub(r"\s+", " ", clean_name).strip().strip(".,")
        
        if not clean_name: continue
        if any(c in clean_name for c in '&+|@'): 
            extracted_affiliations.append(line)
            continue
            
        words = clean_name.split()
        if not (2 <= len(words) <= 6):
            # Probably an affiliation or junk
            extracted_affiliations.append(line)
            continue
            
        particles = {'van', 'de', 'der', 'la', 'von', 'di', 'del', 'le', 'al', 'bin', 'ibn', 'da', 'dos', 'das'}
        is_valid = True
        for w in words:
            w_lower = w.lower().strip('.,')
            if w_lower in blacklist: 
                is_valid = False
                break
            if not (w[0].isupper() or w_lower in particles or len(w) <= 2):
                is_valid = False
                break
                
        if is_valid:
            extracted_authors.append(clean_name)
        else:
            extracted_affiliations.append(line)
            
    return deduped_emails, extracted_authors, extracted_affiliations

print("Test 1: 2212.00193v2")
print(parse_metadata([
    "Distilling Reasoning Capabilities into Smaller Language Models",
    "Kumar Shridhar ∗ Alessandro Stolfo ∗ Mrinmaya Sachan",
    "Department of Computer Science, ETH Z¨ urich",
    "{ shkumar, stolfoa } @ethz.ch"
]))

print("Test 2: 2212.00196v2")
print(parse_metadata([
    "Hamish Ivison α Noah A. Smith αβ Hannaneh Hajishirzi αβ α",
    "Allen Institute for AI",
    "β Paul G. Allen School of Computer Science & Engineering, University of Washington {hamishi,noah,hannah,pradeepd}@allenai.org"
]))

print("Test 3: Multiple affiliations")
print(parse_metadata([
    "University of Pennsylvania 2 University of California, Berkeley 3 Google Research, Brain Team"
]))

