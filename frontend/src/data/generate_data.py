import json

central_categories = [
  {"id": 'defence', "name": '🛡️ Defence', "slug": 'defence'},
  {"id": 'police', "name": '👮 Police & Paramilitary', "slug": 'police'},
  {"id": 'banking', "name": '🏦 Banking & Finance', "slug": 'banking'},
  {"id": 'railways', "name": '📡 Railways', "slug": 'railways'},
  {"id": 'teaching', "name": '🎓 Teaching', "slug": 'teaching'},
  {"id": 'civil-services', "name": '🏛️ Civil Services', "slug": 'civil-services'},
  {"id": 'healthcare', "name": '⚕️ Healthcare', "slug": 'healthcare'},
  {"id": 'engineering', "name": '🔬 Engineering / Technical', "slug": 'engineering'},
  {"id": 'postal', "name": '📮 Postal / Other', "slug": 'postal'}
]

state_categories = [
  {"id": 'civil-services', "name": '🏛️ Civil Services', "slug": 'civil-services'},
  {"id": 'police', "name": '👮 Police', "slug": 'police'},
  {"id": 'teaching', "name": '🎓 Teaching', "slug": 'teaching'},
  {"id": 'banking', "name": '🏦 Banking / Cooperative', "slug": 'banking'},
  {"id": 'judiciary', "name": '⚖️ Judiciary', "slug": 'judiciary'},
  {"id": 'technical', "name": '🔬 Technical / Engineering', "slug": 'technical'},
  {"id": 'healthcare', "name": '🏥 Healthcare', "slug": 'healthcare'},
  {"id": 'postal', "name": '📮 Other State PSU', "slug": 'postal'}
]

raw_data = [
    # Central - Defence
    ('nda', 'NDA (National Defence Academy)', 'UPSC', 'defence', 'central', 'April & September'),
    ('cds', 'CDS (Combined Defence Services)', 'UPSC', 'defence', 'central', 'April & September'),
    ('afcat', 'AFCAT', 'Indian Air Force', 'defence', 'central', 'February & August'),
    ('navy-aa-ssr', 'Indian Navy AA/SSR', 'Indian Navy', 'defence', 'central', 'May'),
    ('coast-guard', 'Coast Guard Navik', 'Indian Coast Guard', 'defence', 'central', 'March'),
    ('army-tes', 'Indian Army TES', 'Indian Army', 'defence', 'central', 'July'),
    ('drdo-cejt', 'DRDO CEPTAM', 'DRDO', 'defence', 'central', 'November'),
    ('asssam-rifles', 'Assam Rifles Rally', 'Assam Rifles', 'defence', 'central', 'December'),
    
    # Central - Banking
    ('sbi-po', 'SBI PO', 'SBI', 'banking', 'central', 'November'),
    ('ibps-po', 'IBPS PO', 'IBPS', 'banking', 'central', 'October'),
    ('ibps-clerk', 'IBPS Clerk', 'IBPS', 'banking', 'central', 'September'),
    ('rbi-grade-b', 'RBI Grade B', 'RBI', 'banking', 'central', 'July'),
    ('nabard-grade-a', 'NABARD Grade A', 'NABARD', 'banking', 'central', 'August'),
    ('sbi-clerk', 'SBI Clerk', 'SBI', 'banking', 'central', 'January'),
    ('lic-aao', 'LIC AAO', 'LIC', 'banking', 'central', 'March'),
    ('niacl-ao', 'NIACL AO', 'NIACL', 'banking', 'central', 'September'),

    # Central - Railways
    ('rrb-ntpc', 'RRB NTPC', 'RRB', 'railways', 'central', 'May – August'),
    ('rrb-group-d', 'RRB Group D', 'RRB', 'railways', 'central', 'September – December'),
    ('rrb-alp', 'RRB ALP', 'RRB', 'railways', 'central', 'June'),
    ('rrb-je', 'RRB JE', 'RRB', 'railways', 'central', 'July'),
    ('rrb-mi', 'RRB Ministerial & Isolated', 'RRB', 'railways', 'central', 'December'),
    ('rpf-si', 'RPF SI', 'RRB', 'railways', 'central', 'October'),
    ('rpf-constable', 'RPF Constable', 'RRB', 'railways', 'central', 'November'),
    ('dfccil', 'DFCCIL Executive', 'DFCCIL', 'railways', 'central', 'August'),

    # Central - Civil Services
    ('upsc-cse', 'UPSC Civil Services (IAS)', 'UPSC', 'civil-services', 'central', 'May (Prelims)'),
    ('upsc-ifs', 'UPSC Indian Forest Service', 'UPSC', 'civil-services', 'central', 'May (Prelims)'),
    ('upsc-ies', 'UPSC IES / ISS', 'UPSC', 'civil-services', 'central', 'June'),
    ('upsc-cms', 'UPSC Combined Medical Services', 'UPSC', 'civil-services', 'central', 'July'),
    ('ssc-cgl', 'SSC CGL', 'SSC', 'civil-services', 'central', 'August – September'),
    ('ib-acio', 'IB ACIO', 'MHA', 'civil-services', 'central', 'February'),
    ('upsc-epfo', 'UPSC EPFO', 'UPSC', 'civil-services', 'central', 'July'),
    ('fci-manager', 'FCI Manager', 'FCI', 'civil-services', 'central', 'January'),

    # Central - Teaching
    ('ctet', 'CTET', 'CBSE', 'teaching', 'central', 'July & December'),
    ('kvs-prt-tgt-pgt', 'KVS PRT/TGT/PGT', 'KVS', 'teaching', 'central', 'February'),
    ('nvs', 'NVS Exam', 'NVS', 'teaching', 'central', 'December'),
    ('dsssb-tgt', 'DSSSB TGT', 'DSSSB', 'teaching', 'central', 'August'),
    ('ugc-net', 'UGC NET', 'NTA', 'teaching', 'central', 'June & December'),
    ('csir-net', 'CSIR NET', 'NTA', 'teaching', 'central', 'June & December'),
    ('awes-aps', 'Army Public School', 'AWES', 'teaching', 'central', 'November'),
    ('emrs', 'EMRS Teaching Staff', 'NTA', 'teaching', 'central', 'October'),

    # Central - Engineering
    ('gate', 'GATE', 'IISc/IITs', 'engineering', 'central', 'February'),
    ('barc', 'BARC OCES/DGFS', 'BARC', 'engineering', 'central', 'April'),
    ('drdo-set', 'DRDO SET', 'DRDO', 'engineering', 'central', 'September'),
    ('isro-scientist', 'ISRO Scientist/Engineer', 'ISRO', 'engineering', 'central', 'January'),
    ('ssc-je', 'SSC JE', 'SSC', 'engineering', 'central', 'October'),
    ('aai-atc', 'AAI ATC', 'AAI', 'engineering', 'central', 'December'),
    ('ongc-gt', 'ONGC Graduate Trainee', 'ONGC', 'engineering', 'central', 'June'),
    ('ntpc-et', 'NTPC Engineering Executive', 'NTPC', 'engineering', 'central', 'July'),

    # Central - Police
    ('ssc-cpo', 'SSC CPO', 'SSC', 'police', 'central', 'October'),
    ('capf-ac', 'UPSC CAPF AC', 'UPSC', 'police', 'central', 'August'),
    ('delhi-police-hc', 'Delhi Police Head Constable', 'SSC', 'police', 'central', 'September'),
    ('cisf-hc', 'CISF Head Constable', 'CISF', 'police', 'central', 'July'),
    ('crpf-tradesman', 'CRPF Constable Tradesman', 'CRPF', 'police', 'central', 'July'),
    ('bsf-ro-rm', 'BSF RO/RM', 'BSF', 'police', 'central', 'November'),
    ('ssb-constable', 'SSB Constable', 'SSB', 'police', 'central', 'May'),
    ('itbp-tele', 'ITBP Telecom', 'ITBP', 'police', 'central', 'September'),

    # Central - Postal & Other
    ('india-post-gds', 'India Post GDS', 'India Post', 'postal', 'central', 'June & December (Merit Base)'),
    ('ssc-chsl', 'SSC CHSL', 'SSC', 'postal', 'central', 'July – August'),
    ('ssc-mts', 'SSC MTS', 'SSC', 'postal', 'central', 'September'),
    ('ssc-stenographer', 'SSC Stenographer C & D', 'SSC', 'postal', 'central', 'October'),
    ('ssc-gd', 'SSC GD Constable', 'SSC', 'postal', 'central', 'February – March'),
    ('isro-assistant', 'ISRO Assistant / UDC', 'ISRO', 'postal', 'central', 'December'),
    ('niacl-assistant', 'NIACL Assistant', 'NIACL', 'postal', 'central', 'April'),
    ('esic-udc', 'ESIC UDC / MTS', 'ESIC', 'postal', 'central', 'March'),
    
    # Central - Healthcare
    ('aiims-norcet', 'AIIMS NORCET', 'AIIMS', 'healthcare', 'central', 'June & September'),
    ('esic-nursing', 'ESIC Nursing Officer', 'ESIC', 'healthcare', 'central', 'May'),
    ('rrb-paramedical', 'RRB Paramedical', 'RRB', 'healthcare', 'central', 'July'),
    ('cghs-pharmacist', 'CGHS Pharmacist', 'CGHS', 'healthcare', 'central', 'August'),
    ('dsssb-nursing', 'DSSSB Nursing Officer', 'DSSSB', 'healthcare', 'central', 'September'),
    ('itbp-medical', 'ITBP Medical Officer', 'ITBP', 'healthcare', 'central', 'October'),
    ('military-nursing', 'MNS (Military Nursing Service)', 'Indian Army', 'healthcare', 'central', 'January'),
    ('upsc-cmo', 'UPSC CMO', 'UPSC', 'healthcare', 'central', 'July'),

    # State - Civil Services
    ('tnpsc-group-1', 'TNPSC Group 1', 'TNPSC', 'civil-services', 'state', 'July'),
    ('tnpsc-group-2', 'TNPSC Group 2 & 2A', 'TNPSC', 'civil-services', 'state', 'August'),
    ('tnpsc-group-4', 'TNPSC Group 4 (CCSE IV)', 'TNPSC', 'civil-services', 'state', 'June'),
    ('tnpsc-group-3', 'TNPSC Group 3', 'TNPSC', 'civil-services', 'state', 'October'),
    ('tnpsc-group-7b', 'TNPSC Group 7B', 'TNPSC', 'civil-services', 'state', 'November'),
    ('tnpsc-group-8', 'TNPSC Group 8', 'TNPSC', 'civil-services', 'state', 'December'),
    ('mha-tn', 'TN Secretariat Assistant', 'TNPSC', 'civil-services', 'state', 'February'),
    ('tn-audit', 'Audit Inspector', 'TNPSC', 'civil-services', 'state', 'March'),

    # State - Police
    ('tnusrb-si', 'TNUSRB Sub-Inspector', 'TNUSRB', 'police', 'state', 'August'),
    ('tnusrb-constable', 'TNUSRB Constable', 'TNUSRB', 'police', 'state', 'November'),
    ('jail-warder', 'Jail Warder', 'TNUSRB', 'police', 'state', 'December'),
    ('fireman', 'Fireman (TN)', 'TNUSRB', 'police', 'state', 'December'),
    ('tn-fingerprint', 'Fingerprint SI', 'TNUSRB', 'police', 'state', 'June'),
    ('tn-technical-si', 'Technical SI', 'TNUSRB', 'police', 'state', 'September'),
    ('tn-forest-guard', 'Forest Guard', 'TNFUSRC', 'police', 'state', 'October'),
    ('tn-forest-watcher', 'Forest Watcher', 'TNFUSRC', 'police', 'state', 'February'),

    # State - Teaching
    ('tn-tet', 'TN TET Paper 1 & 2', 'TRB', 'teaching', 'state', 'June & August'),
    ('tn-teachers-recruitment', 'TN TRB PG Assistant', 'TRB', 'teaching', 'state', 'September'),
    ('tnset', 'TNSET', 'Mother Teresa Women’s University', 'teaching', 'state', 'March'),
    ('trb-polytechnic', 'TRB Polytechnic Lecturer', 'TRB', 'teaching', 'state', 'May'),
    ('trb-engineering', 'TRB Engineering College Lecturer', 'TRB', 'teaching', 'state', 'July'),
    ('trb-block-edu', 'BEO (Block Educational Officer)', 'TRB', 'teaching', 'state', 'November'),
    ('trb-special-edu', 'Special Educators TRB', 'TRB', 'teaching', 'state', 'January'),
    ('tn-art-craft', 'Art & Craft Teacher', 'TRB', 'teaching', 'state', 'April'),

    # State - Technical
    ('tangedco-ae', 'TANGEDCO Assistant Engineer', 'TNEB', 'technical', 'state', 'April'),
    ('tangedco-field-assistant', 'TANGEDCO Field Assistant', 'TNEB', 'technical', 'state', 'May'),
    ('twad-board-ae', 'TWAD Board AE', 'TWAD', 'technical', 'state', 'July'),
    ('tneb-assessor', 'TNEB Assessor', 'TNEB', 'technical', 'state', 'August'),
    ('tnpsc-ae', 'TNPSC Combined Engineering Services', 'TNPSC', 'technical', 'state', 'June'),
    ('hw-ae', 'Highways Department AE', 'TNPSC', 'technical', 'state', 'June'),
    ('pwd-ae', 'PWD AE', 'TNPSC', 'technical', 'state', 'June'),
    ('tn-pollution-board', 'TNPCB Assistant Engineer', 'TNPCB', 'technical', 'state', 'September'),

    # State - Healthcare
    ('tn-mrb-nurse', 'TN MRB Staff Nurse', 'MRB', 'healthcare', 'state', 'July'),
    ('pharmacist', 'Pharmacist (TN MRB)', 'MRB', 'healthcare', 'state', 'August'),
    ('lab-technician', 'Lab Technician Grade II', 'MRB', 'healthcare', 'state', 'September'),
    ('tnmsc', 'TNMSC Assistant', 'TNMSC', 'healthcare', 'state', 'October'),
    ('mrb-doctor', 'Assistant Surgeon (General)', 'MRB', 'healthcare', 'state', 'March'),
    ('mrb-vho', 'Village Health Nurse', 'MRB', 'healthcare', 'state', 'December'),
    ('mrb-radio', 'Radiographer', 'MRB', 'healthcare', 'state', 'November'),
    ('mrb-physio', 'Physiotherapist', 'MRB', 'healthcare', 'state', 'February'),
    
    # State - Banking
    ('tnsc-bank', 'TNSC Bank Assistant', 'TNSC Bank', 'banking', 'state', 'May'),
    ('tn-coop-bank', 'Cooperative Bank Clerk', 'TN Cooperative Board', 'banking', 'state', 'June'),
    ('repco-bank', 'Repco Bank PO', 'Repco', 'banking', 'state', 'August'),
    ('repco-clerk', 'Repco Bank Clerk', 'Repco', 'banking', 'state', 'September'),
    ('tiic-manager', 'TIIC Manager', 'TIIC', 'banking', 'state', 'July'),
    ('tiic-officer', 'TIIC Senior Officer', 'TIIC', 'banking', 'state', 'October'),
    ('tnfc', 'TNFC Assistant', 'TNFC', 'banking', 'state', 'December'),
    ('tafcoon', 'TAFCOn Assistant', 'TAFCOn', 'banking', 'state', 'January'),

    # State - Judiciary
    ('mhc-examiner', 'MHC Examiner/Reader', 'Madras High Court', 'judiciary', 'state', 'May'),
    ('tn-civil-judge', 'TN Civil Judge', 'TNPSC', 'judiciary', 'state', 'September'),
    ('mhc-assistant', 'MHC Assistant', 'Madras High Court', 'judiciary', 'state', 'July'),
    ('mhc-typist', 'MHC Typist', 'Madras High Court', 'judiciary', 'state', 'August'),
    ('district-court', 'District Court Office Assistant', 'District Courts', 'judiciary', 'state', 'November'),
    ('tn-app', 'Assistant Public Prosecutor', 'TNPSC', 'judiciary', 'state', 'February'),
    ('mhc-office-asst', 'MHC Office Assistant', 'Madras High Court', 'judiciary', 'state', 'June'),
    ('family-court', 'Family Court Counselor', 'Madras High Court', 'judiciary', 'state', 'January'),
    
    # State - Postal (Other State PSU instead)
    ('tasmac', 'TASMAC Assistant', 'TASMAC', 'postal', 'state', 'July'),
    ('cmrl', 'CMRL Manager/Exec', 'CMRL', 'postal', 'state', 'May'),
    ('tidco', 'TIDCO Assistant', 'TIDCO', 'postal', 'state', 'March'),
    ('avin', 'Aavin Executive', 'Aavin', 'postal', 'state', 'August'),
    ('avin-tech', 'Aavin Technician', 'Aavin', 'postal', 'state', 'September'),
    ('tnstc', 'TNSTC Driver/Conductor', 'TNSTC', 'postal', 'state', 'December'),
    ('tn-housing', 'TNHB Assistant', 'TNHB', 'postal', 'state', 'October'),
    ('tn-slum', 'TNSCB Engineer', 'TNSCB', 'postal', 'state', 'November')
]

LINK_MAP = {
    'UPSC': 'https://upsconline.nic.in',
    'SSC': 'https://ssc.nic.in',
    'SBI': 'https://sbi.co.in/web/careers',
    'IBPS': 'https://ibps.in',
    'RBI': 'https://opportunities.rbi.org.in',
    'NABARD': 'https://nabard.org/careers',
    'RRB': 'https://indianrailways.gov.in/railwayboard/view_section.jsp?lang=0&id=0,4,1244',
    'CBSE': 'https://ctet.nic.in',
    'KVS': 'https://kvsangathan.nic.in',
    'NVS': 'https://navodaya.gov.in',
    'DSSSB': 'https://dsssbonline.nic.in',
    'NTA': 'https://nta.ac.in',
    'BARC': 'https://barconlineexam.in',
    'ISRO': 'https://isro.gov.in/careers',
    'DRDO': 'https://drdo.gov.in/careers',
    'TNPSC': 'https://apply.tnpscexams.in',
    'TNUSRB': 'https://tnusrb.tn.gov.in',
    'TRB': 'https://trb.tn.gov.in',
    'TNEB': 'https://tangedco.gov.in',
    'TWAD': 'https://twadboard.tn.gov.in',
    'MRB': 'https://mrb.tn.gov.in',
    'Madras High Court': 'https://mhc.tn.gov.in',
    'India Post': 'https://indiapostgdsonline.gov.in',
    'ESIC': 'https://esic.gov.in/recruitments',
    'AIIMS': 'https://aiimsexams.ac.in',
    'Indian Navy': 'https://joinindiannavy.gov.in',
    'Indian Army': 'https://joinindianarmy.nic.in',
    'Indian Coast Guard': 'https://joinindiancoastguard.cdac.in',
    'CISF': 'https://cisfrectt.in',
    'CRPF': 'https://rect.crpf.gov.in',
    'BSF': 'https://rectt.bsf.gov.in',
    'SSB': 'https://ssbrectt.gov.in',
    'ITBP': 'https://recruitment.itbpolice.nic.in',
    'MHA': 'https://mha.gov.in/notifications/vacancies',
    'LIC': 'https://licindia.in/Bottom-Links/careers',
    'NIACL': 'https://www.newindia.co.in/portal/readMore/Recruitment',
    'DFCCIL': 'https://dfccil.com/Home/DynemicPages?MenuId=175',
    'FCI': 'https://fci.gov.in/personnel.php?view=333',
    'AWES': 'https://www.awesindia.com',
    'IISc/IITs': 'https://gate.iisc.ac.in',
    'AAI': 'https://www.aai.aero/en/careers/recruitment',
    'ONGC': 'https://ongcindia.com/web/eng/career',
    'NTPC': 'https://careers.ntpc.co.in',
    'TNFUSRC': 'https://www.forests.tn.gov.in/pages/view/TNFUSRC',
    'Mother Teresa Women’s University': 'https://www.motherteresawomenuniv.ac.in',
    'TNPCB': 'https://tnpcb.gov.in',
    'TNMSC': 'https://tnmsc.tn.gov.in',
    'TNSC Bank': 'https://www.tnscbank.com',
    'TN Cooperative Board': 'https://www.tncoopboard.in',
    'Repco': 'https://www.repcobank.com/careers',
    'TIIC': 'https://www.tiic.org/careers',
    'TNFC': 'https://www.tnfc.in',
    'District Courts': 'https://districts.ecourts.gov.in/tamil-nadu',
    'TASMAC': 'https://www.tasmac.co.in',
    'CMRL': 'https://chennaimetrorail.org/careers',
    'TIDCO': 'https://tidco.com/careers',
    'Aavin': 'https://aavin.tn.gov.in/careers',
    'TNSTC': 'https://www.tnstc.in',
    'TNHB': 'https://tnhb.tn.gov.in',
    'TNSCB': 'https://www.tnurbantree.tn.gov.in'
}

exams = []
for i, item in enumerate(raw_data):
    key, name, body, cat, level, month = item
    
    real_link = LINK_MAP.get(body, f"https://www.google.com/search?q={body.replace(' ', '+')}+{name.replace(' ', '+')}+official+website")
    
    exam = {
        "key": key,
        "name": name,
        "conductingBody": body,
        "category": cat,
        "level": level,
        "expectedMonth": month,
        "description": f"Prepare for {name} conducted by {body}. This is a prominent examination in the {cat.replace('-', ' ')} sector.",
        "status": "Upcoming",
        "dates": [
            {"id": "d1", "date_type": "Notification Expected", "date": "1st Week of " + month.split(' ')[0]},
            {"id": "d2", "date_type": "Exam Date", "date": month}
        ],
        "is_open": True,
        "apply_link": real_link,
        "official_link": real_link,
        "vacancies": "1000+",
        "application_start_date": "TBA",
        "application_end_date": "TBA",
        "eligibility": "Candidates must meet the minimum educational qualifications prescribed by the official conducting body. Refer to the official notification for age limits and reservations.",
        "syllabus": {
            "overview": f"The {name} examination follows a structured pattern testing candidates on core competencies.",
            "total_marks": 200,
            "total_questions": 100,
            "duration": "120 Minutes",
            "pattern": "- Objective type questions\\n- Negative marking applicable (0.25 marks per wrong answer)\\n- Multiple stages of selection",
            "subjects": [
                {
                    "name": "General Intelligence & Reasoning",
                    "total_subject_marks": 50,
                    "topics": [
                        {
                            "name": "Logical Reasoning",
                            "subtopics": ["Analogies", "Spatial Visualization", "Problem Solving", "Coding-Decoding"],
                            "marks_weightage": "20 Marks"
                        },
                        {
                            "name": "Analytical Ability",
                            "subtopics": ["Analysis", "Judgment", "Visual Memory", "Decision Making"],
                            "marks_weightage": "30 Marks"
                        }
                    ]
                },
                {
                    "name": "General Awareness",
                    "total_subject_marks": 50,
                    "topics": [
                        {
                            "name": "Current Affairs",
                            "subtopics": ["National Events", "International News", "Sports", "Awards & Honours"],
                            "marks_weightage": "25 Marks"
                        },
                        {
                            "name": "Static GK",
                            "subtopics": ["History", "Culture", "Geography", "Economic Scene", "General Polity", "Scientific Research"],
                            "marks_weightage": "25 Marks"
                        }
                    ]
                },
                {
                    "name": "Quantitative Aptitude / Core Subject",
                    "total_subject_marks": 100,
                    "topics": [
                        {
                            "name": "Arithmetic",
                            "subtopics": ["Number Systems", "Percentages", "Ratio & Proportion", "Averages", "Time & Work"],
                            "marks_weightage": "40 Marks"
                        },
                        {
                            "name": "Advanced Math / Technical",
                            "subtopics": ["Algebra", "Geometry", "Trigonometry", "Core Domain Concepts (if applicable)"],
                            "marks_weightage": "60 Marks"
                        }
                    ]
                }
            ]
        }
    }
    exams.append(exam)

js_content = f"""// Auto-generated static data for Indian Government Exams

export const centralCategories = {json.dumps(central_categories, indent=2)};

export const stateCategories = {json.dumps(state_categories, indent=2)};

export const examsData = {json.dumps(exams, indent=2)};

export const getExamsByLevel = (level) => examsData.filter(exam => exam.level === level);
export const getExamByKey = (key) => examsData.find(exam => exam.key === key);
"""

with open(r'c:\Users\Vignesh S\Music\exam_app-main\frontend\src\data\examsData.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print("examsData.js generated successfully with previous state!")
