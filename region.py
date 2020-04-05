provinsi = {
    "sumatera" : {
        "prov_aceh" : "Aceh", "prov_sumatera_barat" : "Sumatera Barat", "prov_sumatera_selatan" : "Sumatera Selatan",
        "prov_sumatera_utara": "Sumatera Utara", "prov_bengkulu": "Bengkulu", "prov_kepulauan_riau" : "Kepulauan Riau", 
        "prov_riau": "Riau", "prov_lampung" : "Lampung", "prov_bangka_belitung" : "Kepulauan Bangka Belitung", "prov_jambi" : "Jambi"
    },
    "jawa" : {
        "prov_banten": "Banten", "prov_dki_jakarta" : "DKI Jakarta", "prov_jawa_barat" : "Jawa Barat", "prov_yogyakarta" : "DI Yogyakarta", "prov_jawa_tengah" : "Jawa Tengah",
        "prov_jawa_timur" : "Jawa Timur", "prov_bali" : "Bali"
    },
    "kalimantan" : {
        "prov_kalimantan_barat" : "Kalimantan Barat", "prov_kalimantan_tengah" : "Kalimantan Tengah", "prov_kalimantan_timur": "Kalimantan Timur",
        "prov_kalimantan_selatan" : "Kalimantan Selatan"
    },
    "sulawesi" : {
        "prov_gorontalo" : "Gorontalo", "prov_sulawesi_utara" : "Sulawesi Utara", "prov_sulawesi_selatan" : "Sulawesi Selatan", "prov_sulawesi_barat" : "Sulawesi Barat",
        "prov_sulawesi_tengah" : "Sulawesi Tengah", "prov_sulawesi_tenggara" : "Sulawesi Tenggara"
    },
    "nusa_tenggara" : {
        "prov_nusa_tenggara_barat" : "Nusa Tenggara Barat", "prov_nusa_tenggara_timur" : "Nusa Tenggara Timur"
    },
    "maluku" : {
        "prov_maluku" : "Maluku", "prov_maluku_utara" : "Maluku Utara"
    },
    "papua" : {
        "prov_papua" : "Papua", "prov_papua_barat" : "Papua Barat"
    }
}

wilayah = {"sumatera": "Sumatera", "jawa" : "Jawa", "kalimantan" : "kalimantan", "sulawesi": "Sulawesi", "nusa_tenggara" : "Nusa Tenggara", 
"maluku" : "Maluku", "papua" : "Papua"}

prov_all = [
{"id":"11","nama":"ACEH"},
{"id":"12","nama":"SUMATERA UTARA"},
{"id":"13","nama":"SUMATERA BARAT"},
{"id":"14","nama":"RIAU"},
{"id":"15","nama":"JAMBI"},
{"id":"16","nama":"SUMATERA SELATAN"},
{"id":"17","nama":"BENGKULU"},
{"id":"18","nama":"LAMPUNG"},
{"id":"19","nama":"KEPULAUAN BANGKA BELITUNG"},
{"id":"21","nama":"KEPULAUAN RIAU"},
{"id":"22","nama":"BENGKULU"},
{"id":"31","nama":"DKI JAKARTA"},
{"id":"32","nama":"JAWA BARAT"},
{"id":"33","nama":"JAWA TENGAH"},
{"id":"34","nama":"DI YOGYAKARTA"},
{"id":"35","nama":"JAWA TIMUR"},
{"id":"36","nama":"BANTEN"},
{"id":"51","nama":"BALI"},
{"id":"52","nama":"NUSA TENGGARA BARAT"},
{"id":"53","nama":"NUSA TENGGARA TIMUR"},
{"id":"61","nama":"KALIMANTAN BARAT"},
{"id":"62","nama":"KALIMANTAN TENGAH"},
{"id":"63","nama":"KALIMANTAN SELATAN"},
{"id":"64","nama":"KALIMANTAN TIMUR"},
{"id":"65","nama":"KALIMANTAN UTARA"},
{"id":"71","nama":"SULAWESI UTARA"},
{"id":"72","nama":"SULAWESI TENGAH"},
{"id":"73","nama":"SULAWESI SELATAN"},
{"id":"74","nama":"SULAWESI TENGGARA"},
{"id":"75","nama":"GORONTALO"},
{"id":"76","nama":"SULAWESI BARAT"},
{"id":"81","nama":"MALUKU"},
{"id":"82","nama":"MALUKU UTARA"},
{"id":"91","nama":"PAPUA BARAT"},
{"id":"94","nama":"PAPUA"}]


test = [
    {
        "nama" : "sumatera",
        "text" : "Sumatera",
        "provinsi" : [
            {"id":"11","nama":"ACEH"},
            {"id":"12","nama":"SUMATERA UTARA"},
            {"id":"13","nama":"SUMATERA BARAT"},
            {"id":"14","nama":"RIAU"},
            {"id":"15","nama":"JAMBI"},
            {"id":"16","nama":"SUMATERA SELATAN"},{"id":"17","nama":"BENGKULU"},
            {"id":"18","nama":"LAMPUNG"},
            {"id":"19","nama":"KEPULAUAN BANGKA BELITUNG"},
            {"id":"21","nama":"KEPULAUAN RIAU"},
            {"id":"22","nama":"BENGKULU"}
        ]
    },
    {
        "nama" : "jawa",
        "text" : "Jawa",
        "provinsi" : [
            {"id":"31","nama":"DKI JAKARTA"},
            {"id":"32","nama":"JAWA BARAT"},
            {"id":"33","nama":"JAWA TENGAH"},
            {"id":"34","nama":"DI YOGYAKARTA"},
            {"id":"35","nama":"JAWA TIMUR"},
            {"id":"36","nama":"BANTEN"},
            {"id":"51","nama":"BALI"}
        ]
    },
    {
        "nama" : "nusa_tenggara",
        "text" : "Nusa Tenggara",
        "provinsi" : [
            {"id":"52","nama":"NUSA TENGGARA BARAT"},
            {"id":"53","nama":"NUSA TENGGARA TIMUR"}
        ]
    },
    {
        "nama" : "nusa_tenggara",
        "text" : "Nusa Tenggara",
        "provinsi" : [
            {"id":"61","nama":"KALIMANTAN BARAT"},
            {"id":"62","nama":"KALIMANTAN TENGAH"},
            {"id":"63","nama":"KALIMANTAN SELATAN"},
            {"id":"64","nama":"KALIMANTAN TIMUR"},
            {"id":"65","nama":"KALIMANTAN UTARA"}
        ]
    },
    {
        "nama" : "sulawesi",
        "text" : "Sulawesi",
        "provinsi" : [
            {"id":"71","nama":"SULAWESI UTARA"},
            {"id":"72","nama":"SULAWESI TENGAH"},
            {"id":"73","nama":"SULAWESI SELATAN"},
            {"id":"74","nama":"SULAWESI TENGGARA"},
            {"id":"75","nama":"GORONTALO"},
            {"id":"76","nama":"SULAWESI BARAT"}
        ]
    },
    {
        "nama" : "maluku",
        "text" : "Maluku",
        "provinsi" : [
            {"id":"81","nama":"MALUKU"},
            {"id":"82","nama":"MALUKU UTARA"}
        ]
    },
    {
        "nama" : "papua",
        "text" : "Papua",
        "provinsi" : [
            {"id":"91","nama":"PAPUA BARAT"},
            {"id":"94","nama":"PAPUA"}
        ]
    }
]