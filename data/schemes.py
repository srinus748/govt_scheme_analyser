# data/schemes.py - Updated URLs

SCHEMES = [
    # Farmer Schemes
    {
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-Kisan)",
        "description": "Provides income support of Rs. 6,000 per year to all landholding farmer families.",
        "url": "https://pmkisan.gov.in/",  # This URL should work
        "tags": ["farmer", "all"],
        "category": "Agriculture",
        "benefits": "Direct cash transfer of Rs. 6,000 per year in three equal installments",
        "eligibility": "All landholding farmer families with cultivable land",
        "application_process": "Register online through the PM-Kisan portal or visit Common Service Centers"
    },
    {
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "description": "Crop insurance scheme to provide financial support to farmers for crop losses.",
        "url": "https://pmfby.gov.in/",  # This URL should work
        "tags": ["farmer"],
        "category": "Agriculture",
        "benefits": "Insurance coverage and financial support against crop loss due to natural calamities",
        "eligibility": "All farmers including sharecroppers and tenant farmers growing notified crops",
        "application_process": "Apply through banks, insurance companies, or Common Service Centers"
    },
    {
        "name": "Soil Health Card Scheme",
        "description": "Provides farmers with soil health cards to help them apply nutrients accordingly.",
        "url": "https://soilhealth.dac.gov.in/",  # This URL should work
        "tags": ["farmer"],
        "category": "Agriculture",
        "benefits": "Soil health analysis and recommendations for nutrient application",
        "eligibility": "All farmers across the country",
        "application_process": "Register at local agriculture office or through the Soil Health Card portal"
    },
    {
        "name": "e-NAM (National Agriculture Market)",
        "description": "Online trading platform for agricultural commodities to ensure better price discovery.",
        "url": "https://enam.gov.in/",  # This URL should work
        "tags": ["farmer"],
        "category": "Agriculture",
        "benefits": "Better price realization for agricultural produce through transparent online trading",
        "eligibility": "All farmers and traders in agricultural commodities",
        "application_process": "Register on the e-NAM portal through local mandi authorities"
    },
    {
        "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "description": "Promotes organic farming and provides financial assistance for conversion to organic methods.",
        "url": "https://pgsindia-ncof.gov.in/",  # This URL should work
        "tags": ["farmer"],
        "category": "Agriculture",
        "benefits": "Financial assistance of Rs. 20,000 per hectare for organic farming",
        "eligibility": "Farmers willing to adopt organic farming practices",
        "application_process": "Apply through cluster approach at district agriculture office"
    },
    
    # Student Schemes
    {
        "name": "National Scholarship Portal (NSP)",
        "description": "One-stop platform for various scholarship schemes offered by central and state governments.",
        "url": "https://scholarships.gov.in/",  # This URL should work
        "tags": ["student"],
        "category": "Education",
        "benefits": "Financial assistance for education at various levels",
        "eligibility": "Students from economically weaker sections, minorities, and meritorious students",
        "application_process": "Apply online through the National Scholarship Portal"
    },
    {
        "name": "Pragati Scholarship Scheme",
        "description": "Scholarship for girl students to encourage technical education.",
        "url": "https://www.aicte-india.org/schemes/students-development-schemes/pragati-scholarship-scheme",  # Updated URL
        "tags": ["student", "woman"],
        "category": "Education",
        "benefits": "Rs. 30,000 per annum and other benefits for girl students in technical education",
        "eligibility": "Girl students admitted to AICTE approved institutions in first year",
        "application_process": "Apply online through the AICTE portal"
    },
    {
        "name": "Saksham Scholarship Scheme",
        "description": "Scholarship for differently-abled students to encourage technical education.",
        "url": "https://www.aicte-india.org/schemes/students-development-schemes/saksham-scholarship-scheme",  # Updated URL
        "tags": ["student"],
        "category": "Education",
        "benefits": "Rs. 30,000 per annum and other benefits for differently-abled students",
        "eligibility": "Differently-abled students admitted to AICTE approved institutions",
        "application_process": "Apply online through the AICTE portal"
    },
    {
        "name": "Prime Minister's Scholarship Scheme for Central Armed Police Forces & Assam Rifles",
        "description": "Scholarship for wards of CAPF & Assam Rifles personnel.",
        "url": "https://welfare.gov.in/",  # Updated URL
        "tags": ["student"],
        "category": "Education",
        "benefits": "Financial assistance for higher education",
        "eligibility": "Wards of CAPF & Assam Rifles personnel",
        "application_process": "Apply through the respective welfare organizations"
    },
    {
        "name": "INSPIRE Scholarship",
        "description": "Scholarship for higher education in basic sciences.",
        "url": "https://www.inspire-dst.gov.in/",  # This URL should work
        "tags": ["student"],
        "category": "Education",
        "benefits": "Scholarship value of Rs. 80,000 per annum for 5 years",
        "eligibility": "Top 1% students in class 12th board exams pursuing B.Sc./M.Sc. in Natural Sciences",
        "application_process": "Apply online through the INSPIRE portal"
    },
    
    # Women Schemes
    {
        "name": "Beti Bachao, Beti Padhao",
        "description": "Scheme to save and educate the girl child.",
        "url": "https://betibachao.betipadhao.gov.in/",  # This URL should work
        "tags": ["woman", "student"],
        "category": "Women & Child Development",
        "benefits": "Awareness and support for girl child education and welfare",
        "eligibility": "All girl children across the country",
        "application_process": "Various initiatives at district and block levels"
    },
    {
        "name": "Sukanya Samriddhi Yojana",
        "description": "Savings scheme for the girl child to ensure her education and marriage expenses.",
        "url": "https://www.sukanyasamriddhi.gov.in/",  # This URL should work
        "tags": ["woman"],
        "category": "Women & Child Development",
        "benefits": "High interest rate savings account with tax benefits",
        "eligibility": "Girl child below 10 years of age",
        "application_process": "Open account at authorized bank branches or post offices"
    },
    {
        "name": "Mahila Shakti Kendra",
        "description": "Community-based support for empowering rural women.",
        "url": "https://mwcd.gov.in/schemes/mahila-shakti-kendra",  # Updated URL
        "tags": ["woman"],
        "category": "Women & Child Development",
        "benefits": "Skill development, employment opportunities, and support services",
        "eligibility": "Rural women across the country",
        "application_process": "Register at the nearest Mahila Shakti Kendra"
    },
    {
        "name": "Working Women Hostel",
        "description": "Provides safe and affordable accommodation for working women.",
        "url": "https://mwcd.gov.in/schemes/working-women-hostel",  # Updated URL
        "tags": ["woman", "worker"],
        "category": "Women & Child Development",
        "benefits": "Safe and affordable accommodation with daycare facilities",
        "eligibility": "Working women with income up to a specified limit",
        "application_process": "Apply through the respective state government authorities"
    },
    {
        "name": "SWADHAR Greh Scheme",
        "description": "Support system for women in difficult circumstances.",
        "url": "https://mwcd.gov.in/schemes/swadhar-greh",  # Updated URL
        "tags": ["woman"],
        "category": "Women & Child Development",
        "benefits": "Shelter, food, clothing, and support services",
        "eligibility": "Women in difficult circumstances without social or economic support",
        "application_process": "Contact the nearest SWADHAR Greh center"
    },
    
    # Worker Schemes
    {
        "name": "Pradhan Mantri Shram Yogi Maan-Dhan (PM-SYM)",
        "description": "Pension scheme for unorganized sector workers.",
        "url": "https://maandhan.in/",  # This URL should work
        "tags": ["worker"],
        "category": "Labor & Employment",
        "benefits": "Minimum assured pension of Rs. 3,000 per month after age 60",
        "eligibility": "Unorganized sector workers aged 18-40 with monthly income up to Rs. 15,000",
        "application_process": "Register through Common Service Centers or online portal"
    },
    {
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
        "description": "Life insurance scheme for all bank account holders.",
        "url": "https://pmjdy.gov.in/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Finance",
        "benefits": "Life insurance cover of Rs. 2 lakh at an annual premium of Rs. 330",
        "eligibility": "Bank account holders aged 18-50 years",
        "application_process": "Register through bank branches"
    },
    {
        "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
        "description": "Accident insurance scheme for all bank account holders.",
        "url": "https://pmjdy.gov.in/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Finance",
        "benefits": "Accident insurance cover of Rs. 2 lakh for death/disability at Rs. 12 per year",
        "eligibility": "Bank account holders aged 18-70 years",
        "application_process": "Register through bank branches"
    },
    {
        "name": "Atal Pension Yojana (APY)",
        "description": "Pension scheme for unorganized sector workers.",
        "url": "https://www.nps-trust.org.in/APY/",  # This URL should work
        "tags": ["worker"],
        "category": "Finance",
        "benefits": "Fixed pension of Rs. 1,000-5,000 per month after age 60",
        "eligibility": "Citizens of India aged 18-40 years with a bank account",
        "application_process": "Register through bank branches"
    },
    {
        "name": "Employees' Provident Fund (EPF)",
        "description": "Retirement benefit scheme for organized sector employees.",
        "url": "https://www.epfindia.gov.in/",  # This URL should work
        "tags": ["worker"],
        "category": "Labor & Employment",
        "benefits": "Retirement benefits, pension, and insurance coverage",
        "eligibility": "Organized sector employees with basic salary up to Rs. 15,000 per month",
        "application_process": "Registration through employer"
    },
    
    # Senior Citizen Schemes
    {
        "name": "Pradhan Mantri Vaya Vandana Yojana (PMVVY)",
        "description": "Pension scheme for senior citizens.",
        "url": "https://www.licindia.in/pmvvy",  # This URL should work
        "tags": ["senior"],
        "category": "Finance",
        "benefits": "Assured pension of Rs. 3,000-10,000 per month for 10 years",
        "eligibility": "Senior citizens aged 60 years and above",
        "application_process": "Purchase policy from Life Insurance Corporation of India"
    },
    {
        "name": "Varishtha Pension Bima Yojana (VPBY)",
        "description": "Pension scheme for senior citizens.",
        "url": "https://www.licindia.in/",  # This URL should work
        "tags": ["senior"],
        "category": "Finance",
        "benefits": "Monthly pension based on purchase amount",
        "eligibility": "Senior citizens aged 60 years and above",
        "application_process": "Purchase policy from Life Insurance Corporation of India"
    },
    {
        "name": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        "description": "Pension scheme for destitute elderly persons.",
        "url": "https://nsap.gov.in/",  # This URL should work
        "tags": ["senior"],
        "category": "Social Security",
        "benefits": "Monthly pension of Rs. 200-500 for elderly persons below poverty line",
        "eligibility": "Persons aged 60 years and above belonging to BPL category",
        "application_process": "Apply through local government authorities"
    },
    {
        "name": "Senior Citizens' Welfare Fund",
        "description": "Welfare fund for senior citizens' healthcare and other needs.",
        "url": "https://socialjustice.nic.in/",  # This URL should work
        "tags": ["senior"],
        "category": "Social Security",
        "benefits": "Financial support for healthcare and other needs of senior citizens",
        "eligibility": "Senior citizens aged 60 years and above",
        "application_process": "Apply through the Ministry of Social Justice and Empowerment"
    },
    
    # Health Schemes
    {
        "name": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
        "description": "Health insurance scheme for poor and vulnerable families.",
        "url": "https://pmjay.gov.in/",  # This URL should work
        "tags": ["all"],
        "category": "Health",
        "benefits": "Health coverage of Rs. 5 lakh per family per year for secondary and tertiary care",
        "eligibility": "Poor and vulnerable families as per SECC data",
        "application_process": "Check eligibility and enroll at empaneled hospitals"
    },
    {
        "name": "Pradhan Mantri Swasthya Suraksha Yojana (PMSSY)",
        "description": "Scheme to improve healthcare infrastructure in the country.",
        "url": "https://www.pmssy-mohfw.nic.in/",  # This URL should work
        "tags": ["all"],
        "category": "Health",
        "benefits": "Improved healthcare facilities through AIIMS and other medical institutions",
        "eligibility": "All citizens benefitting from improved healthcare infrastructure",
        "application_process": "Direct benefit through improved healthcare facilities"
    },
    {
        "name": "National Health Mission (NHM)",
        "description": "Mission to provide universal access to equitable, affordable and quality healthcare services.",
        "url": "https://nhm.gov.in/",  # This URL should work
        "tags": ["all"],
        "category": "Health",
        "benefits": "Improved healthcare delivery system and health outcomes",
        "eligibility": "All citizens of India",
        "application_process": "Direct benefit through improved healthcare facilities"
    },
    
    # Housing Schemes
    {
        "name": "Pradhan Mantri Awas Yojana (Urban)",
        "description": "Housing for All - Urban mission to provide affordable housing.",
        "url": "https://pmaymis.gov.in/",  # This URL should work
        "tags": ["worker", "woman", "all"],
        "category": "Housing",
        "benefits": "Interest subsidy on home loans and financial assistance for house construction",
        "eligibility": "Urban poor including economically weaker sections and low-income groups",
        "application_process": "Apply through the PMAY-U portal or urban local bodies"
    },
    {
        "name": "Pradhan Mantri Awas Yojana (Gramin)",
        "description": "Housing for All - Rural mission to provide affordable housing.",
        "url": "https://pmayg.nic.in/",  # This URL should work
        "tags": ["worker", "woman", "all"],
        "category": "Housing",
        "benefits": "Financial assistance of Rs. 1.20 lakh for construction of house",
        "eligibility": "Rural households without pucca house",
        "application_process": "Apply through the PMAY-G portal or local government authorities"
    },
    {
        "name": "Rajiv Awas Yojana (RAY)",
        "description": "Scheme for slum-free India.",
        "url": "https://mhupa.gov.in/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Housing",
        "benefits": "Development of slums and provision of affordable housing",
        "eligibility": "Slum dwellers across the country",
        "application_process": "Apply through urban local bodies"
    },
    
    # Business & Entrepreneurship Schemes
    {
        "name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "description": "Scheme to provide loans up to Rs. 10 lakh to non-corporate, non-farm small/micro enterprises.",
        "url": "https://www.mudra.org.in/",  # This URL should work
        "tags": ["worker", "woman", "all"],
        "category": "Business & Finance",
        "benefits": "Loans up to Rs. 10 lakh without collateral for business activities",
        "eligibility": "Non-corporate, non-farm small/micro enterprises",
        "application_process": "Apply through banks, NBFCs, MFIs, and other financial institutions"
    },
    {
        "name": "Stand Up India Scheme",
        "description": "Scheme to promote entrepreneurship among women and SC/ST communities.",
        "url": "https://www.standupmitra.in/",  # This URL should work
        "tags": ["woman", "worker"],
        "category": "Business & Finance",
        "benefits": "Bank loans between Rs. 10 lakh and Rs. 1 crore for greenfield enterprises",
        "eligibility": "Women and SC/ST entrepreneurs for setting up greenfield enterprises",
        "application_process": "Apply through scheduled banks"
    },
    {
        "name": "Startup India",
        "description": "Scheme to promote startups and provide them with a conducive environment.",
        "url": "https://www.startupindia.gov.in/",  # This URL should work
        "tags": ["worker", "student", "all"],
        "category": "Business & Finance",
        "benefits": "Tax benefits, easier compliance, funding support, and other incentives",
        "eligibility": "Startups recognized by DPIIT",
        "application_process": "Register on the Startup India portal"
    },
    {
        "name": "Make in India",
        "description": "Initiative to encourage companies to manufacture in India.",
        "url": "https://www.makeinindia.com/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Business & Finance",
        "benefits": "Improved business environment and investment opportunities",
        "eligibility": "All businesses and entrepreneurs",
        "application_process": "Direct benefit through improved business environment"
    },
    
    # Rural Development Schemes
    {
        "name": "Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)",
        "description": "Scheme to provide guaranteed wage employment in rural areas.",
        "url": "https://nrega.nic.in/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Rural Development",
        "benefits": "Guaranteed 100 days of wage employment in a financial year",
        "eligibility": "Adult members of rural households willing to do unskilled manual work",
        "application_process": "Register at local Gram Panchayat"
    },
    {
        "name": "Deendayal Antyodaya Yojana - National Rural Livelihoods Mission (DAY-NRLM)",
        "description": "Scheme to promote self-employment and organization of rural poor.",
        "url": "https://aajeevika.gov.in/",  # This URL should work
        "tags": ["worker", "woman"],
        "category": "Rural Development",
        "benefits": "Financial assistance, skill development, and livelihood opportunities",
        "eligibility": "Rural poor households",
        "application_process": "Register through Self Help Groups (SHGs)"
    },
    {
        "name": "National Rural Livelihood Mission (NRLM)",
        "description": "Scheme to promote self-employment and organization of rural poor.",
        "url": "https://aajeevika.gov.in/",  # This URL should work
        "tags": ["worker", "woman"],
        "category": "Rural Development",
        "benefits": "Financial assistance, skill development, and livelihood opportunities",
        "eligibility": "Rural poor households",
        "application_process": "Register through Self Help Groups (SHGs)"
    },
    
    # Urban Development Schemes
    {
        "name": "Smart Cities Mission",
        "description": "Mission to promote cities that provide core infrastructure and a decent quality of life.",
        "url": "https://smartcities.gov.in/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Urban Development",
        "benefits": "Improved urban infrastructure and quality of life",
        "eligibility": "Citizens of selected smart cities",
        "application_process": "Direct benefit through improved urban infrastructure"
    },
    {
        "name": "Atal Mission for Rejuvenation and Urban Transformation (AMRUT)",
        "description": "Mission to provide basic services like water supply, sewerage, and transport.",
        "url": "https://amrut.gov.in/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Urban Development",
        "benefits": "Improved basic urban services and infrastructure",
        "eligibility": "Citizens of selected cities/towns",
        "application_process": "Direct benefit through improved urban infrastructure"
    },
    {
        "name": "Swachh Bharat Mission (Urban)",
        "description": "Mission to achieve universal sanitation coverage and make India clean.",
        "url": "https://swachhbharaturban.gov.in/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Urban Development",
        "benefits": "Improved sanitation and waste management in urban areas",
        "eligibility": "All urban citizens",
        "application_process": "Direct benefit through improved sanitation facilities"
    },
    
    # Financial Inclusion Schemes
    {
        "name": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
        "description": "Financial inclusion scheme to ensure access to financial services.",
        "url": "https://pmjdy.gov.in/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Finance",
        "benefits": "Bank account with RuPay debit card, overdraft facility, and insurance cover",
        "eligibility": "All Indian citizens without a bank account",
        "application_process": "Open account at any bank branch or Bank Mitra outlet"
    },
    {
        "name": "Pradhan Mantri Garib Kalyan Yojana (PMGKY)",
        "description": "Scheme to provide relief to the poor during COVID-19 pandemic.",
        "url": "https://www.pmgky.in/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Social Security",
        "benefits": "Free LPG cylinders, food grains, and other relief measures",
        "eligibility": "Poor and vulnerable families",
        "application_process": "Direct benefit through existing delivery mechanisms"
    },
    
    # Digital India Schemes
    {
        "name": "Digital India",
        "description": "Initiative to transform India into a digitally empowered society.",
        "url": "https://digitalindia.gov.in/",  # This URL should work
        "tags": ["student", "worker", "all"],
        "category": "Digital Services",
        "benefits": "Improved digital infrastructure and services",
        "eligibility": "All citizens of India",
        "application_process": "Direct benefit through improved digital services"
    },
    {
        "name": "Common Service Centers (CSCs)",
        "description": "Scheme to provide access to various government services at the village level.",
        "url": "https://digitalseva.csc.gov.in/",  # This URL should work
        "tags": ["worker", "all"],
        "category": "Digital Services",
        "benefits": "Access to various government services at the village level",
        "eligibility": "All citizens of India",
        "application_process": "Visit the nearest Common Service Center"
    },
    {
        "name": "DigiLocker",
        "description": "Platform for issuance and verification of documents and certificates.",
        "url": "https://digilocker.gov.in/",  # This URL should work
        "tags": ["student", "worker", "all"],
        "category": "Digital Services",
        "benefits": "Digital wallet for storing and sharing documents",
        "eligibility": "All citizens of India",
        "application_process": "Register on the DigiLocker portal"
    }
]