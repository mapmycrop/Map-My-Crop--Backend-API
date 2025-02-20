import enum


class Role(enum.Enum):
    farmer = "farmer"
    agronomist = "agronomist"
    superadmin = "superadmin"
    advisor = "advisor"


class HowToContact(enum.Enum):
    whatsapp = "whatsapp"
    zoom = "zoom"
    phone = "phone"


class ContactSource(enum.Enum):
    Web = "Web"
    Mobile = "Mobile"


class RegisterSource(enum.Enum):
    Web = "Web"
    Mobile = "Mobile"


class ScoutingStatus(enum.Enum):
    open = "open"
    in_progress = "in progress"
    closed = "closed"


class Topic(enum.Enum):
    general = "general"
    disease = "disease"
    plantation = "plantation"
    harvesting = "harvesting"
    pesticides = "pesticides"
    waste = "waste"


class Maturity(enum.Enum):
    early = "early"
    mid = "mid"
    late = "late"


class IrrigationType(enum.Enum):
    center_pivot = "center pivot"
    drip = "drip"
    horse_end = "horse end"
    sprinkler = "sprinkler"
    micro = "micro"
    canal = "canal"
    borewell = "borewell"
    other = "other"


class TillageType(enum.Enum):
    no_till = "no till"
    intense = "intense"
    conservation = "conservation"


class TypeOfExpert(enum.Enum):
    local = "local"
    international = "international"


class SocialLoginProviderType(enum.Enum):
    none = "none"
    google = "google"
    facebook = "facebook"


class LogSource(enum.Enum):
    web = "web"
    android = "android"
    ios = "ios"
    api = "api"


STATES = [
    "Karnataka",
    "Kerala",
    "Bihar",
    "Chattisgarh",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jammu and Kashmir",
    "Andhra Pradesh",
    "Tamil Nadu",
    "Telangana",
    "Maharashtra",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Uttar Pradesh",
    "Madhya Pradesh",
    "Uttrakhand",
    "West Bengal",
    "Meghalaya",
]

DISTRICTS = [
    "Bangalore",
    "Chamrajnagar",
    "Hassan",
    "Kolar",
    "Koppal",
    "Mandya",
    "Mysore",
    "Shimoga",
    "Alappuzha",
    "Kishanganj",
    "Madhepura",
    "Nalanda",
    "Nawada",
    "West Chambaran",
    "Dhamtari",
    "Kabirdham",
    "Kanker",
    "Rajnandgaon",
    "Sukma",
    "Amreli",
    "Banaskanth",
    "Bharuch",
    "Dahod",
    "Gandhinagar",
    "Jamnagar",
    "Junagarh",
    "Patan",
    "Porbandar",
    "Rajkot",
    "Sabarkantha",
    "Surendranagar",
    "Vadodara(Baroda)",
    "Valsad",
    "Faridabad",
    "Fatehabad",
    "Gurgaon",
    "Kurukshetra",
    "Mahendragarh-Narnaul",
    "Mewat",
    "Rewari",
    "Sonipat",
    "Yamuna Nagar",
    "Ernakulam",
    "Idukki",
    "Kannur",
    "Kasargod",
    "Kozhikode(Calicut)",
    "Malappuram",
    "Palakad",
    "Kullu",
    "Shimla",
    "Sirmore",
    "Solan",
    "Anantnag",
    "Jammu",
    "Bilaspur",
    "Chamba",
    "Kangra",
    "Kollam",
    "Kottayam",
    "Chittor",
    "Guntur",
    "Kurnool",
    "Bhagalpur",
    "Thiruvannamalai",
    "Villupuram",
    "Adilabad",
    "Hyderabad",
    "Karimnagar",
    "Khammam",
    "Medak",
    "Nalgonda",
    "Nizamabad",
    "Ranga Reddy",
    "Mumbai",
    "Nagpur",
    "Parbhani",
    "Pune",
    "Satara",
    "Thane",
    "Kohima",
    "Dhenkanal",
    "Gajapati",
    "Jajpur",
    "Malkangiri",
    "Ludhiana",
    "Mansa",
    "Mohali",
    "Patiala",
    "Ropar (Rupnagar)",
    "Sangrur",
    "Tarntaran",
    "Thirssur",
    "Thiruvananthapuram",
    "Hanumangarh",
    "Jaipur",
    "Jalore",
    "Jhunjunu",
    "Jodhpur",
    "Kota",
    "Tonk",
    "Coimbatore",
    "Erode",
    "Namakkal",
    "Warangal",
    "Agra",
    "Aligarh",
    "Allahabad",
    "Ambedkarnagar",
    "Badaun",
    "Bahraich",
    "Ballia",
    "Balrampur",
    "Banda",
    "Barabanki",
    "Amritsar",
    "Bhatinda",
    "Fatehgarh",
    "Fazilka",
    "Gurdaspur",
    "Hoshiarpur",
    "Jalandhar",
    "kapurthala",
    "Wayanad",
    "Gwalior",
    "Khargone",
    "Rajgarh",
    "Shajapur",
    "Ahmednagar",
    "Kolhapur",
    "Ghaziabad",
    "Ghazipur",
    "Gonda",
    "Gorakhpur",
    "Hamirpur",
    "Hardoi",
    "Hathras",
    "Bulandshahar",
    "Etawah",
    "Farukhabad",
    "Fatehpur",
    "Jalaun (Orai)",
    "Jaunpur",
    "Jhansi",
    "Kannuj",
    "Kanpur",
    "Bareilly",
    "Basti",
    "Bijnor",
    "Muzaffarnagar",
    "Pillibhit",
    "Pratapgarh",
    "Raebarelli",
    "Firozabad",
    "Gautam Budh Nagar",
    "Maharajganj",
    "Mainpuri",
    "Mathura",
    "Mau(Maunathbhanjan)",
    "Mirzapur",
    "Muradabad",
    "Rampur",
    "Saharanpur",
    "Shahjahanpur",
    "Shravasti",
    "Khiri (Lakhimpur)",
    "Lakhimpur",
    "Lalitpur",
    "Lucknow",
    "Siddharth Nagar",
    "Sitapur",
    "Sultanpur",
    "Unnao",
    "Dehradoon",
    "Haridwar",
    "Nanital",
    "UdhamSinghNagar",
    "Bankura",
    "Burdwan",
    "Coochbehar",
    "Hooghly",
    "Jalpaiguri",
    "Mandi",
    "Kaithal",
    "Madikeri(Kodagu)",
    "Panchkula",
    "Jashpur",
    "Koria",
    "Ashoknagar",
    "Salem",
    "Thanjavur",
    "Ajmer",
    "Barmer",
    "Bharatpur",
    "Jagityal",
    "Mahbubnagar",
    "Chandrapur",
    "Jalgaon",
    "East Khasi Hills",
    "Etah",
    "Malda",
    "Mehsana",
    "Durg",
    "Sirsa",
    "East Godavari",
    "Raigad",
    "Dausa",
    "Dewas",
    "Bhojpur",
    "Kaimur/Bhabhua",
    "Raichur",
    "Indore",
    "Jhabua",
    "Nashik",
    "Chittorgarh",
    "Bargarh",
    "Mahoba",
    "Surajpur",
    "Kheda",
    "Jehanabad",
    "Dindigul",
]

COMMODITIES = [
    "Brinjal",
    "Cabbage",
    "Seemebadnekai",
    "Beetroot",
    "Green Chilli",
    "Raddish",
    "Elephant Yam (Suran)",
    "Maize",
    "Carrot",
    "Potato",
    "Cowpea (Lobia/Karamani)",
    "Tender Coconut",
    "Bitter gourd",
    "Cauliflower",
    "Drumstick",
    "Snakeguard",
    "Tomato",
    "Arhar Dal(Tur Dal)",
    "Cucumbar(Kheera)",
    "Green Gram Dal (Moong Dal)",
    "Methi Seeds",
    "Ragi (Finger Millet)",
    "Rice",
    "Ridgeguard(Tori)",
    "Tamarind Fruit",
    "Amphophalus",
    "Banana",
    "Banana - Green",
    "Cowpea(Veg)",
    "Pumpkin",
    "Amaranthus",
    "Colacasia",
    "Onion",
    "Mousambi(Sweet Lime)",
    "Papaya",
    "Field Pea",
    "Paddy(Dhan)(Common)",
    "Lemon",
    "Castor Seed",
    "Bajra(Pearl Millet/Cumbu)",
    "Ginger(Green)",
    "Onion Green",
    "Surat Beans (Papadi)",
    "Cotton",
    "Jowar(Sorghum)",
    "Bengal Gram(Gram)(Whole)",
    "Bhindi(Ladies Finger)",
    "French Beans (Frasbean)",
    "Garlic",
    "Arhar (Tur/Red Gram)(Whole)",
    "Sesamum(Sesame,Gingelly,Til)",
    "Wheat",
    "Beans",
    "Cummin Seed(Jeera)",
    "Chikoos(Sapota)",
    "Green Gram (Moong)(Whole)",
    "Guava",
    "Kulthi(Horse Gram)",
    "Groundnut",
    "Coriander(Leaves)",
    "Black Gram (Urd Beans)(Whole)",
    "Methi(Leaves)",
    "Bottle gourd",
    "Grapes",
    "Pomegranate",
    "Capsicum",
    "Kinnow",
    "Apple",
    "Spinach",
    "Tinda",
    "Tapioca",
    "Mango (Raw-Ripe)",
    "Ashgourd",
    "Cluster beans",
    "Little gourd (Kundru)",
    "Pineapple",
    "Coconut Seed",
    "Peas Wet",
    "Leafy Vegetable",
    "Orange",
    "Turnip",
    "Ber(Zizyphus/Borehannu)",
    "Indian Colza(Sarson)",
    "Coconut",
    "Turmeric",
    "T.V. Cumbu",
    "Carnation",
    "Chow Chow",
    "Kakada",
    "Knool Khol",
    "Wood",
    "Chilly Capsicum",
    "Guar",
    "Sweet Potato",
    "Soyabean",
    "Lime",
    "Ginger(Dry)",
    "Guar Seed(Cluster Beans Seed)",
    "Corriander seed",
    "Copra",
    "Karbuja(Musk Melon)",
    "Mustard",
    "Black Gram Dal (Urd Dal)",
    "Gur(Jaggery)",
    "White Peas",
    "Mashrooms",
    "Peas cod",
    "Pepper ungarbled",
    "Bengal Gram Dal (Chana Dal)",
    "Lentil (Masur)(Whole)",
    "Mustard Oil",
    "Peas(Dry)",
    "Green Peas",
    "Paddy(Dhan)(Basmati)",
    "Masur Dal",
    "Pointed gourd (Parval)",
    "Sweet Pumpkin",
    "Indian Beans (Seam)",
    "Black pepper",
    "Papaya (Raw)",
    "Green Avare (W)",
    "Kabuli Chana(Chickpeas-White)",
    "Rubber",
    "Squash(Chappal Kadoo)",
    "Season Leaves",
    "Ground Nut Seed",
    "Arecanut(Betelnut/Supari)",
    "Thondekai",
    "Mango",
    "Duster Beans",
    "Coffee",
    "Water Melon",
    "Dry Chillies",
    "Marigold(loose)",
    "Turmeric (raw)",
    "Astera",
    "Gladiolus Cut Flower",
    "Jasmine",
    "Sabu Dan",
    "Mint(Pudina)",
    "Tobacco",
    "Barley (Jau)",
    "Coconut Oil",
    "Pegeon Pea (Arhar Fali)",
    "Suvarna Gadde",
    "Yam (Ratalu)",
    "Moath Dal",
    "Taramira",
    "Rose(Loose))",
    "Chili Red",
    "Jack Fruit",
    "Sugar",
    "Round gourd",
    "Long Melon(Kakri)",
    "Kodo Millet(Varagu)",
    "Jarbara",
    "Kankambra",
    "Firewood",
    "Jute",
    "Millets",
    "Sponge gourd",
    "Yam",
    "Hen",
    "Lilly",
    "Marigold(Calcutta)",
    "Amla(Nelli Kai)",
    "Betal Leaves",
]
