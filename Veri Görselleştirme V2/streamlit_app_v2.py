# -*- coding: utf-8 -*-
"""
Created on Sat May  9 09:59:26 2026

@author: ergun
"""

"""
Dünya Bankası Göstergeleri Keşif Aracı — Streamlit Eğitim Demosu
Çalıştırmak için terminale şunu yazın:  streamlit run streamlit_app.py
"""

# =========================================================================
# 1. KÜTÜPHANE İÇE AKTARIMLARI (IMPORTS)
# =========================================================================
# Streamlit: Yazdığımız standart Python kodunu saniyeler içinde web uygulamasına dönüştürür.
import streamlit as st
# Pandas: Veri okuma, filtreleme, birleştirme ve şekillendirme (ağır işçilik) için kullanılır.
import pandas as pd
# Numpy: Matematiksel işlemler (örn. logaritmik dönüşüm, sıfıra bölme hatalarını önleme) için.
import numpy as np
# Plotly Express: 1-2 satır kodla etkileşimli, yayına hazır kaliteli grafikler sunar.
import plotly.express as px

# OS: Dosya yollarını (CSV dosyalarının yerini) dinamik ve hatasız bulmak için kullanılır.
import os 

# =========================================================================
# 2. SAYFA YAPILANDIRMASI (PAGE CONFIGURATION)
# =========================================================================
# ÖNEMLİ BİLGİ: `st.set_page_config` komutu her zaman betikteki İLK Streamlit komutu olmalıdır!
# Tarayıcı sekme başlığını, ikonu, sayfa genişliğini ve yan menünün başlangıç durumunu ayarlar.
st.set_page_config(
    page_title="Dünya Bankası Keşif Aracı", # Tarayıcı sekmesinde görünecek başlık
    page_icon="🌍",                        # Favicon (Emoji veya görsel yolu kullanılabilir)
    layout="wide",                         # 'wide': Uygulamanın tüm ekran genişliğini kullanmasını sağlar
    initial_sidebar_state="expanded",      # Yan menü (sidebar) başlangıçta açık gelsin
)

# =========================================================================
# 3. ÖZEL CSS (TASARIM DOKUNUŞLARI)
# =========================================================================
# Streamlit, `st.markdown(unsafe_allow_html=True)` ile HTML/CSS enjekte etmemize izin verir.
# Püf Noktası: Bunu idareli kullanın! Çok fazla özel CSS, Streamlit güncellendiğinde uygulamanızı bozabilir.
st.markdown(
    """
    <style>
    /* Üst boşluğu daraltarak sayfa başlığının tarayıcı kenarına daha yakın oturmasını sağlarız */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    /* Metrik (KPI) kartlarına hafif bir kenarlık ve yuvarlak köşeler ekleyerek modernleştiriyoruz */
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    /* Metrik etiketlerini biraz daha kalın fontla yazdırıyoruz */
    [data-testid="stMetricLabel"] { font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================================
# 4. SABİTLER (CONSTANTS) — Ülke ve Bölge Meta Verileri
# =========================================================================
# Dünya Bankası veri setleri hem gerçek ülkeleri hem de "Arap Dünyası", "OECD Üyeleri" gibi 
# bölgesel/gelir gruplarını aynı sütunda karışık verir. Harita çiziminde (choropleth) 
# sadece geçerli bir ISO-3 kodu olan gerçek ülkeleri görmek isteriz. Bu yüzden iki arama tablosu kuruyoruz.

# 4a. Ülke bazlı görünümlerde HARİÇ TUTULACAK (EXCLUDE) bölgesel gruplar (53 adet).
AGGREGATES = {
    "Africa Eastern and Southern", "Africa Western and Central", "Arab World",
    "Caribbean small states", "Central Europe and the Baltics", "Channel Islands",
    "Early-demographic dividend", "East Asia & Pacific",
    "East Asia & Pacific (IDA & IBRD countries)",
    "East Asia & Pacific (excluding high income)", "Euro area",
    "Europe & Central Asia", "Europe & Central Asia (IDA & IBRD countries)",
    "Europe & Central Asia (excluding high income)", "European Union",
    "Fragile and conflict affected situations",
    "Heavily indebted poor countries (HIPC)", "High income",
    "IBRD only", "IDA & IBRD total", "IDA blend", "IDA only", "IDA total",
    "Late-demographic dividend", "Latin America & Caribbean",
    "Latin America & Caribbean (excluding high income)",
    "Latin America & the Caribbean (IDA & IBRD countries)",
    "Least developed countries: UN classification", "Low & middle income",
    "Low income", "Lower middle income", "Middle East & North Africa",
    "Middle East & North Africa (IDA & IBRD countries)",
    "Middle East & North Africa (excluding high income)",
    "Middle East, North Africa, Afghanistan & Pakistan",
    "Middle East, North Africa, Afghanistan & Pakistan (IDA & IBRD)",
    "Middle East, North Africa, Afghanistan & Pakistan (excluding high income)",
    "Middle income", "North America", "Not classified", "OECD members",
    "Other small states", "Pacific island small states",
    "Post-demographic dividend", "Pre-demographic dividend",
    "Small states", "South Asia", "South Asia (IDA & IBRD)",
    "Sub-Saharan Africa", "Sub-Saharan Africa (IDA & IBRD countries)",
    "Sub-Saharan Africa (excluding high income)", "Upper middle income", "World",
}

# 4b. Ülke İsimleri → ISO-3 Kodları eşleştirmesi (216 ülke).
# Plotly'nin dünya haritası doğru çalışmak için ISO-3 kodlarına (örn: TUR, USA) ihtiyaç duyar.
# DB isimleri bazen farklı yazıldığı için ("Korea, Rep." vb.) çalışma zamanında hata almamak adına
# bu eşleştirmeyi manuel bir sözlük (dictionary) olarak saklıyoruz.
ISO3 = {
    "Aruba": "ABW", "Afghanistan": "AFG", "Angola": "AGO", "Albania": "ALB",
    "Andorra": "AND", "United Arab Emirates": "ARE", "Argentina": "ARG",
    "Armenia": "ARM", "American Samoa": "ASM", "Antigua and Barbuda": "ATG",
    "Australia": "AUS", "Austria": "AUT", "Azerbaijan": "AZE", "Burundi": "BDI",
    "Belgium": "BEL", "Benin": "BEN", "Burkina Faso": "BFA", "Bangladesh": "BGD",
    "Bulgaria": "BGR", "Bahrain": "BHR", "Bahamas, The": "BHS",
    "Bosnia and Herzegovina": "BIH", "Belarus": "BLR", "Belize": "BLZ",
    "Bermuda": "BMU", "Bolivia": "BOL", "Brazil": "BRA", "Barbados": "BRB",
    "Brunei Darussalam": "BRN", "Bhutan": "BTN", "Botswana": "BWA",
    "Central African Republic": "CAF", "Canada": "CAN", "Switzerland": "CHE",
    "Chile": "CHL", "China": "CHN", "Cote d'Ivoire": "CIV", "Cameroon": "CMR",
    "Congo, Dem. Rep.": "COD", "Congo, Rep.": "COG", "Colombia": "COL",
    "Comoros": "COM", "Cabo Verde": "CPV", "Costa Rica": "CRI", "Cuba": "CUB",
    "Curacao": "CUW", "Cayman Islands": "CYM", "Cyprus": "CYP",
    "Czech Republic": "CZE", "Czechia": "CZE", "Germany": "DEU", "Djibouti": "DJI",
    "Dominica": "DMA", "Denmark": "DNK", "Dominican Republic": "DOM",
    "Algeria": "DZA", "Ecuador": "ECU", "Egypt, Arab Rep.": "EGY",
    "Eritrea": "ERI", "Spain": "ESP", "Estonia": "EST", "Ethiopia": "ETH",
    "Finland": "FIN", "Fiji": "FJI", "France": "FRA", "Faroe Islands": "FRO",
    "Micronesia, Fed. Sts.": "FSM", "Gabon": "GAB", "United Kingdom": "GBR",
    "Georgia": "GEO", "Ghana": "GHA", "Gibraltar": "GIB", "Guinea": "GIN",
    "Guadeloupe": "GLP", "Gambia, The": "GMB", "Guinea-Bissau": "GNB",
    "Equatorial Guinea": "GNQ", "Greece": "GRC", "Grenada": "GRD",
    "Greenland": "GRL", "Guatemala": "GTM", "Guam": "GUM", "Guyana": "GUY",
    "Hong Kong SAR, China": "HKG", "Honduras": "HND", "Croatia": "HRV",
    "Haiti": "HTI", "Hungary": "HUN", "Indonesia": "IDN", "Isle of Man": "IMN",
    "India": "IND", "Ireland": "IRL", "Iran, Islamic Rep.": "IRN", "Iraq": "IRQ",
    "Iceland": "ISL", "Israel": "ISR", "Italy": "ITA", "Jamaica": "JAM",
    "Jordan": "JOR", "Japan": "JPN", "Kazakhstan": "KAZ", "Kenya": "KEN",
    "Kyrgyz Republic": "KGZ", "Cambodia": "KHM", "Kiribati": "KIR",
    "St. Kitts and Nevis": "KNA", "Korea, Rep.": "KOR", "Kuwait": "KWT",
    "Lao PDR": "LAO", "Lebanon": "LBN", "Liberia": "LBR", "Libya": "LBY",
    "St. Lucia": "LCA", "Liechtenstein": "LIE", "Sri Lanka": "LKA",
    "Lesotho": "LSO", "Lithuania": "LTU", "Luxembourg": "LUX", "Latvia": "LVA",
    "Macao SAR, China": "MAC", "St. Martin (French part)": "MAF",
    "Morocco": "MAR", "Monaco": "MCO", "Moldova": "MDA", "Madagascar": "MDG",
    "Maldives": "MDV", "Mexico": "MEX", "Marshall Islands": "MHL",
    "North Macedonia": "MKD", "Mali": "MLI", "Malta": "MLT", "Myanmar": "MMR",
    "Montenegro": "MNE", "Mongolia": "MNG", "Northern Mariana Islands": "MNP",
    "Mozambique": "MOZ", "Mauritania": "MRT", "Mauritius": "MUS", "Malawi": "MWI",
    "Malaysia": "MYS", "Namibia": "NAM", "New Caledonia": "NCL", "Niger": "NER",
    "Nigeria": "NGA", "Nicaragua": "NIC", "Netherlands": "NLD", "Norway": "NOR",
    "Nepal": "NPL", "Nauru": "NRU", "New Zealand": "NZL", "Oman": "OMN",
    "Pakistan": "PAK", "Panama": "PAN", "Peru": "PER", "Philippines": "PHL",
    "Palau": "PLW", "Papua New Guinea": "PNG", "Poland": "POL",
    "Puerto Rico (US)": "PRI", "Korea, Dem. People's Rep.": "PRK",
    "Portugal": "PRT", "Paraguay": "PRY", "West Bank and Gaza": "PSE",
    "French Polynesia": "PYF", "Qatar": "QAT", "Romania": "ROU",
    "Russian Federation": "RUS", "Rwanda": "RWA", "Saudi Arabia": "SAU",
    "Sudan": "SDN", "Senegal": "SEN", "Singapore": "SGP",
    "Solomon Islands": "SLB", "Sierra Leone": "SLE", "El Salvador": "SLV",
    "San Marino": "SMR", "Somalia, Fed. Rep.": "SOM", "Serbia": "SRB",
    "South Sudan": "SSD", "Sao Tome and Principe": "STP", "Suriname": "SUR",
    "Slovak Republic": "SVK", "Slovenia": "SVN", "Sweden": "SWE", "Eswatini": "SWZ",
    "Sint Maarten (Dutch part)": "SXM", "Seychelles": "SYC",
    "Syrian Arab Republic": "SYR", "Turks and Caicos Islands": "TCA", "Chad": "TCD",
    "Togo": "TGO", "Thailand": "THA", "Tajikistan": "TJK", "Turkmenistan": "TKM",
    "Timor-Leste": "TLS", "Tonga": "TON", "Trinidad and Tobago": "TTO",
    "Tunisia": "TUN", "Türkiye": "TUR", "Turkiye": "TUR", "Tuvalu": "TUV", "Tanzania": "TZA",
    "Uganda": "UGA", "Ukraine": "UKR", "Uruguay": "URY", "United States": "USA",
    "Uzbekistan": "UZB", "St. Vincent and the Grenadines": "VCT",
    "Venezuela, RB": "VEN", "British Virgin Islands": "VGB", "Virgin Islands (U.S.)": "VIR",
    "Vietnam": "VNM", "Viet Nam": "VNM", "Vanuatu": "VUT", "Samoa": "WSM", "Kosovo": "XKX",
    "Yemen, Rep.": "YEM", "South Africa": "ZAF", "Zambia": "ZMB", "Zimbabwe": "ZWE",
}

# =========================================================================
# 5. VERİ YÜKLEME (ÖNBELLEKLEME - CACHING İLE)
# =========================================================================
# DİKKAT: `@st.cache_data` dekoratörü Streamlit performansının kalbidir.
# Bu fonksiyonun sonucunu RAM'e kaydeder. Böylece CSV dosyaları her etkileşimde (örn.
# kullanıcı slider'ı çektiğinde) baştan okunmaz, saniyenin milyonda biri sürede RAM'den getirilir.
@st.cache_data(show_spinner="Dünya Bankası verileri yükleniyor…")
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    
    # app.py dosyasının bulunduğu klasörün tam yolunu otomatik olarak buluyoruz
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
   # CSV dosyalarının tam yollarını bu klasör yolu ile birleştirerek oluşturuyoruz
    gdp_path = os.path.join(current_dir, 'Worldbank GDP Data_v3.csv')
    pop_path = os.path.join(current_dir, 'Worldbank Population Data_v3.csv')
    area_path = os.path.join(current_dir, 'Worldbank Country Area_v3.csv')
    
    # Dosyaları okuyoruz (Eğer dosyalar sekmeyle ayrılmışsa delimiter="\t" parametresi önemlidir)
    gdp = pd.read_csv(gdp_path,  delimiter = "\t") 
    pop = pd.read_csv(pop_path, delimiter = "\t")
    area = pd.read_csv(area_path) 
    
    gdp.ffill(inplace=True)
    pop.ffill(inplace=True)
    area.ffill(inplace=True)
    
    return gdp, pop, area


# Yüklenen "Geniş" (Wide) formatlı veri setlerini değişkenlere atıyoruz.
# Önbellekleme sayesinde bu işlem ilk çalıştırmadan sonra anında gerçekleşir.
gdp_w, pop_w, area_w = load_data()


# Yardımcı Fonksiyon: Geniş formattan Uzun (Long) formata dönüştürücü.
# Neden? Çünkü Plotly Express ve Pandas birleştirme (merge) işlemleri Uzun formatta çok daha kolay çalışır.
@st.cache_data
def to_long(wide: pd.DataFrame, value_name: str) -> pd.DataFrame:
    """Geniş (yıllar × ülkeler) veri setini Uzun (Yıl, Ülke, Değer) formata çevirir (Pivot/Melt işlemi)."""
    return (wide.reset_index()
                .melt(id_vars="Year", var_name="Country", value_name=value_name)
                .dropna(subset=[value_name])) # Değeri boş olan (NaN) satırları düşür


# Her üç göstergeyi (GSYİH, Nüfus, Yüzölçümü) yan yana tek bir panel (tablo) haline getiririz.
@st.cache_data
def build_panel() -> pd.DataFrame:
    """GSYİH, Nüfus ve Yüzölçümü verilerini tek bir tabloda birleştirir ve yeni metrikler üretir."""
    g = to_long(gdp_w, "GDP")
    p = to_long(pop_w, "Population")
    a = to_long(area_w, "Area")
    
    # outer merge: Yıl ve Ülke sütunlarını baz alarak tabloları birbiri üzerine diker
    panel = g.merge(p, on=["Year", "Country"], how="outer") \
             .merge(a, on=["Year", "Country"], how="outer")
             
    # Yeni Metrik Üretimi: Kişi Başı GSYİH ($) ve Nüfus Yoğunluğu (kişi / km²).
    # `np.where` kullanımı önemlidir: Nüfus veya Yüzölçümü 0 ise NaN atayarak "Sıfıra Bölme" (Divide-by-zero) hatasını önleriz.
    panel["GDP per capita"] = np.where(panel["Population"] > 0,
                                       panel["GDP"] / panel["Population"], np.nan)
    panel["Pop. density"]   = np.where(panel["Area"] > 0,
                                       panel["Population"] / panel["Area"], np.nan)
                                       
    # ISO-3 kodlarını tabloya ekliyoruz (Bölgesel veriler için NaN dönecektir).
    panel["ISO3"] = panel["Country"].map(ISO3)
    
    # 'IsCountry' adında bir True/False (Boolean) sütun oluşturuyoruz. 
    # Bu satır AGGREGATES listesinde YALSA (Gerçek ülkeyse) True döner. Filtrelemelerde çok işe yarayacak.
    panel["IsCountry"] = ~panel["Country"].isin(AGGREGATES)
    
    return panel


panel = build_panel()

# =========================================================================
# 6. YAN MENÜ (SIDEBAR) — Küresel filtreler ve kontroller
# =========================================================================
# `with st.sidebar:` bloğu içine yazdığımız her şey sayfanın solundaki dar panele yerleşir.
with st.sidebar:
    st.header("⚙️ Kontrol Paneli")

    # ---- Ülke Seçici (Country Picker) ---------------------------------------------------
    # `multiselect` kullanıcıdan liste tipinde (list[str]) veri alır. Ekran boş kalmasın diye varsayılan (default) değerler veriyoruz.
    country_options = sorted(panel.loc[panel["IsCountry"], "Country"].unique())
    default_countries = ["United States", "China", "Germany", "Japan",
                         "India", "Brazil", "Turkiye"]
    countries = st.multiselect(
        "Karşılaştırılacak Ülkeler",
        options=country_options,
        default=[c for c in default_countries if c in country_options],
        help="Trend grafiğinde kıyaslamak için dilediğiniz kadar ülke seçebilirsiniz.",
    )

    # ---- Yıl Aralığı (Year range slider) -----------------------------------------------
    # `slider` a başlangıç değeri (value) olarak bir tuple (min, max) verirsek "Aralık (Range) Slider"ına dönüşür.
    year_min, year_max = int(panel["Year"].min()), int(panel["Year"].max())
    year_range = st.slider(
        "Zaman Aralığı", min_value=year_min, max_value=year_max,
        value=(2000, year_max),  # Varsayılan olarak 2000'den günümüze kadar göster
        step=1,
    )

    # ---- Ana Metrik Seçici (Headline metric selector) ----------------------------------------
    # `selectbox` açılır bir listeden TEK bir seçenek seçmek için kullanılır.
    metric = st.selectbox(
        "İncelenecek Metrik",
        options=["GDP", "Population", "GDP per capita", "Pop. density"],
        index=0,
        help="KPI kartlarında, çubuk grafikte ve haritada baz alınacak ana veriyi seçin.",
    )

    # ---- Eksen Ölçeği (Linear / Log scale toggle) ---------------------------------------
    # `radio` butonlarında `horizontal=True` dersek alt alta değil yan yana dizilirler.
    scale = st.radio("Y-Ekseni Ölçeği", ["Doğrusal (Linear)", "Logaritmik"], horizontal=True)

    # ---- Tasarım Dokunuşu: Kullanıcının vurgu rengini seçmesine izin verelim ------
    # `color_picker` demo yapmak için harikadır — '#1f77b4' gibi HEX (renk) kodu döndürür.
    accent = st.color_picker("Vurgu Rengi Seçin", value="#1f77b4")

    # ---- Gelişmiş Ayarlar (Genişletilebilir Kutu - Expander) ----------------------------
    # `expander`, çok sık kullanılmayan ayarları gizleyerek yan menüyü temiz tutmaya yarar.
    with st.expander("Gelişmiş Ayarlar"):
        top_n = st.number_input(
            "Sıralanacak Ülke Sayısı (Çubuk Grafik)", min_value=5, max_value=30,
            value=15, step=1,
        )
        show_aggregates = st.checkbox(
            "Bölgesel Verileri (Aggregates) Tablolara Ekle", value=False,
            help="'Dünya', 'OECD Üyeleri' gibi toplu veriler varsayılan olarak harita ve tablolarda gizlenmiştir.",
        )

    # ---- Öğrenciler için ufak bir State (Durum) bilgisi ---------
    st.divider()
    st.caption("💡 `st.session_state` sayesinde, tarayıcı sekmesi açık kaldığı sürece yaptığınız tüm seçimler hafızada tutulur.")

# Sayfa boyunca sayıların okunabilirliğini artırmak için oluşturduğumuz formatlayıcı fonksiyonlar.
def fmt_money(x: float) -> str:
    """Para birimlerini kısaltır: $29.2T (Trilyon), $4.5B (Milyar), $920M (Milyon) …"""
    if pd.isna(x): return "—"
    for div, sfx in [(1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if abs(x) >= div:
            return f"${x/div:,.2f}{sfx}"
    return f"${x:,.0f}"

def fmt_int(x: float) -> str:
    """Sayıları (örneğin Nüfusu) kısaltır."""
    if pd.isna(x): return "—"
    if abs(x) >= 1e9:  return f"{x/1e9:,.2f} Milyar"
    if abs(x) >= 1e6:  return f"{x/1e6:,.2f} Milyon"
    if abs(x) >= 1e3:  return f"{x/1e3:,.1f} Bin"
    return f"{x:,.0f}"

# =========================================================================
# 7. BAŞLIK VE ÖZET (KPI) KARTLARI
# =========================================================================
# Ana sayfanın en üstündeki başlık ve kısa açıklama
st.title("🌍 Dünya Bankası Göstergeleri Keşif Aracı")
st.caption(
    "**Streamlit** & **Plotly** kullanılarak geliştirilmiş interaktif eğitim paneli. "
    "Veri Kaynağı: Dünya Bankası Açık Verisi — GSYİH (Mevcut ABD$), Nüfus, Yüzölçümü."
)

# Seçilen yıl aralığının son yılına ait metrikleri ve bir önceki yıla göre (YoY) değişimi hesaplıyoruz.
latest_year = year_range[1]
prev_year = latest_year - 1

# Adil bir "Küresel" toplam alabilmek için bölgesel verileri dışarıda bırakıyoruz (IsCountry == True).
country_panel = panel[panel["IsCountry"]]

def kpi_value(df: pd.DataFrame, col: str, year: int) -> float:
    """Belirli bir yıldaki tüm ülkelerin değerlerini toplar."""
    return df.loc[df["Year"] == year, col].sum(min_count=1)

def kpi_delta(curr: float, prev: float) -> str:
    """st.metric'te göstermek üzere 'Yıldan Yıla Değişim' (YoY) stringi oluşturur."""
    if pd.isna(curr) or pd.isna(prev) or prev == 0:
        return "n/a"
    return f"{(curr/prev - 1) * 100:+.1f}% YoY"

# `st.columns(N)` ekranı N adet eşit genişlikte sütuna böler. `with col:` bloğu içindeki
# kodlar o sütunun içine yerleşir. Sayfa düzeni (layout) kurmanın temelidir.
k1, k2, k3, k4 = st.columns(4)

with k1:
    g_now = kpi_value(country_panel, "GDP", latest_year)
    g_prev = kpi_value(country_panel, "GDP", prev_year)
    st.metric("🌐 Küresel GSYİH", fmt_money(g_now), kpi_delta(g_now, g_prev))

with k2:
    p_now = kpi_value(country_panel, "Population", latest_year)
    p_prev = kpi_value(country_panel, "Population", prev_year)
    st.metric("👥 Küresel Nüfus", fmt_int(p_now), kpi_delta(p_now, p_prev))

with k3:
    # Ortalama Kişi Başı GSYİH (Demo olduğu için düz ortalama aldık, gerçekte ağırlıklı ortalama daha iyidir).
    pc_now = country_panel.loc[country_panel["Year"] == latest_year, "GDP per capita"].mean()
    pc_prev = country_panel.loc[country_panel["Year"] == prev_year, "GDP per capita"].mean()
    st.metric("💵 Ort. Kişi Başı Gelir", fmt_money(pc_now), kpi_delta(pc_now, pc_prev))

with k4:
    n_countries = country_panel.loc[country_panel["Year"] == latest_year, "Country"].nunique()
    st.metric("🗺️ Veri Bildiren Ülke", f"{n_countries}", f"{latest_year} Yılında")

st.divider()

# =========================================================================
# 8. SEKMELER (TABS) — Dört ana görünümü organize etme
# =========================================================================
# `st.tabs` girdi olarak verilen isimlerde sekmeler oluşturur. Sayfanın sonsuza kadar
# aşağı uzamasını önlemek ve mantıksal bölümleri ayırmak için mükemmeldir.
tab_trends, tab_map, tab_compare, tab_data = st.tabs([
    "📈 Trendler",
    "🗺️ Dünya Haritası",
    "🏆 Ülke Sıralaması",
    "🗂️ Veri Seti (Explore)",
])

# -------------------------------------------------------------------------
# 8a. TRENDLER SEKMESİ — Seçilen ülkelerin yıllara göre çizgi grafiği
# -------------------------------------------------------------------------
with tab_trends:
    st.subheader(f"Yıllara Göre: {metric}")

    # Ana tabloyu kullanıcının seçtiği ülkelere ve yıl aralığına göre filtrele.
    df_t = panel[
        panel["Country"].isin(countries) &
        panel["Year"].between(year_range[0], year_range[1])
    ].copy()

    if df_t.empty or not countries:
        # `st.info` ve `st.warning` ekranda renkli uyarı/bilgi kutuları oluşturur.
        st.info("👈 Trend grafiğini görebilmek için yan menüden en az bir ülke seçiniz.")
    else:
        # Püf Noktası: Plotly Express lejantı, renkleri, hover (mouse-üzerine gelme) özelliklerini otomatik halleder.
        fig = px.line(
            df_t, x="Year", y=metric, color="Country",
            markers=True,
            template="plotly_white",   # Temiz, beyaz arka planlı tasarım
            color_discrete_sequence=px.colors.qualitative.Bold,
            title=None,
        )
        fig.update_layout(
            height=480,
            hovermode="x unified",  # Aynı yıldaki tüm ülkelerin verisini tek bir hover kutusunda göster
            legend=dict(orientation="h", y=-0.18),  # Lejantı grafiğin altına yatay yerleştir
            margin=dict(l=10, r=10, t=10, b=10),
        )
        # Kullanıcı logaritmik eksen seçtiyse Y eksenini güncelle.
        if scale == "Logarithmic":
            fig.update_yaxes(type="log")
            
        # `use_container_width=True` veya `width="stretch"` grafiği ekrana tam sığdırır.
        st.plotly_chart(fig, use_container_width=True)

        # Çoklu Görünüm (Small Multiples): Tüm ülkeleri tek grafikte karmaşıklaştırmak yerine
        # her ülke için ayrı bir minik grafik çizdirme (Facet) özelliği.
        with st.expander("🔬 Detaylı Görünüm (Her ülke için ayrı panel)"):
            fig2 = px.line(
                df_t, x="Year", y=metric, facet_col="Country", facet_col_wrap=3,
                template="plotly_white", height=120 * (len(countries) // 3 + 1),
                color_discrete_sequence=[accent],  # Kullanıcının yan menüden seçtiği vurgu rengi uygulandı
            )
            # Facet başlıklarındaki gereksiz "Country=" yazısını temizle.
            fig2.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig2.update_layout(showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------------------------------
# 8b. HARİTA SEKMESİ (Choropleth) — Seçili yıla ait verilerin dünya haritasında renklendirilmesi
# -------------------------------------------------------------------------
with tab_map:
    # Bu sekmenin kendisine özel minik bir yıl slider'ı ekliyoruz.
    # `key` parametresi çok önemlidir! Eğer aynı isimde iki widget olursa Streamlit hata verir.
    map_year = st.slider(
        "Haritada gösterilecek yıl",
        min_value=year_range[0], max_value=year_range[1], value=year_range[1],
        key="map_year_slider",  
    )

    # Tabloyu filtrele: Sadece GERÇEK ülkeler, sadece SEÇİLEN yıl ve ISO3 kodu OLANLAR.
    df_m = panel[
        panel["IsCountry"] & (panel["Year"] == map_year) & panel["ISO3"].notna()
    ].copy()

    # Nüfus veya GSYİH gibi aralığı çok geniş olan (1 Milyon ile 1.5 Milyar arası) verilerde
    # renk skalası bozulur (Çin ve Hindistan hariç herkes aynı renk olur). 
    # Logaritmik dönüşüm bu sorunu çözüp renkleri daha iyi dağıtır.
    if scale == "Logarithmic" and metric in ("GDP", "Population", "GDP per capita"):
        df_m["color_value"] = np.log10(df_m[metric].replace(0, np.nan))
        color_label = f"log₁₀({metric})"
    else:
        df_m["color_value"] = df_m[metric]
        color_label = metric

    # choropleth: Ülkeleri ISO-3 kodlarına göre bulup içlerini değere göre renklendiren harita türü
    fig_map = px.choropleth(
        df_m, locations="ISO3", color="color_value",
        hover_name="Country",
        hover_data={
            metric: ":,.0f", "ISO3": False, "color_value": False, # Hoverda sadece asıl metriği göster, log değerini gizle
        },
        color_continuous_scale="Viridis",
        labels={"color_value": color_label},
        template="plotly_white",
    )
    fig_map.update_layout(
        height=560,
        margin=dict(l=0, r=0, t=10, b=0),
        geo=dict(showframe=False, showcoastlines=False, projection_type="natural earth"),
    )
    st.plotly_chart(fig_map, use_container_width=True)

# -------------------------------------------------------------------------
# 8c. TOP-N LİSTESİ SEKMESİ — Yatay çubuk grafik ile sıralama
# -------------------------------------------------------------------------
with tab_compare:
    st.subheader(f"{latest_year} Yılı - Top {top_n} Ülke ({metric})")

    # Veriyi filtreleyip, istenilen metriğe göre en büyük `top_n` adet ülkeyi getiriyoruz
    df_top = (panel[panel["IsCountry"] & (panel["Year"] == latest_year)]
              .dropna(subset=[metric])
              .nlargest(int(top_n), metric)
              .sort_values(metric, ascending=True))   # ascending=True yaptık çünkü Plotly çubukları alttan yukarı dizer

    # orientation="h" ile grafiği yatay (horizontal) yapıyoruz.
    fig_bar = px.bar(
        df_top, x=metric, y="Country", orientation="h",
        text=df_top[metric].apply(
            fmt_money if metric in ("GDP", "GDP per capita") else fmt_int
        ),
        template="plotly_white",
        color=metric, color_continuous_scale="Tealgrn",
    )
    fig_bar.update_layout(
        height=28 * int(top_n) + 80,
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False,
        xaxis_title=metric, yaxis_title=None,
    )
    fig_bar.update_traces(textposition="outside", cliponaxis=False) # Rakamların çubuğun dışına taşmasına izin ver
    if scale == "Logarithmic":
        fig_bar.update_xaxes(type="log")
    st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------------------------------
# 8d. VERİ KEŞİF SEKMESİ — Sıralanabilir tablo ve CSV indirme
# -------------------------------------------------------------------------
with tab_data:
    st.subheader("Filtrelenmiş Ham Veri")

    df_explore = panel.copy()
    if not show_aggregates:
        df_explore = df_explore[df_explore["IsCountry"]]
    df_explore = df_explore[
        df_explore["Year"].between(year_range[0], year_range[1])
    ]
    if countries:
        df_explore = df_explore[df_explore["Country"].isin(countries)]

    # `st.dataframe` oldukça interaktiftir: Başlıklara tıklayıp sıralayabilir, arama yapabilirsiniz.
    # `column_config` kullanarak, asıl veriyi bozmadan ekranda nasıl "görüneceğini" formatlıyoruz.
    st.dataframe(
        df_explore.drop(columns=["IsCountry", "ISO3"]), # Bu sütunları görmelerine gerek yok
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Year":            st.column_config.NumberColumn(format="%d"),
            "GDP":             st.column_config.NumberColumn("GSYİH ($)", format="$%.2e"),
            "Population":      st.column_config.NumberColumn(format="%.0f"),
            "Area":            st.column_config.NumberColumn("Yüzölçümü (km²)", format="%.0f"),
            "GDP per capita":  st.column_config.NumberColumn("Kişi Başı Gelir ($)", format="$%.0f"),
            "Pop. density":    st.column_config.ProgressColumn( # Tablonun içine minik bir ilerleme (progress) çubuğu çizer
                "Nüfus Yoğunluğu (km²)", format="%.1f", min_value=0,
                max_value=float(df_explore["Pop. density"].max() or 1),
            ),
        },
    )

    # İki sütunlu düzen: Solda indirme butonu, sağda özet bilgi.
    dcol, scol = st.columns([1, 2])
    with dcol:
        # `st.download_button` veriyi kullanıcının bilgisayarına indirir.
        # to_csv().encode('utf-8') yapısı Türkçe veya özel karakterlerin bozulmasını engeller.
        st.download_button(
            label="⬇️ Filtrelenmiş Veriyi İndir (CSV)",
            data=df_explore.to_csv(index=False).encode("utf-8"),
            file_name=f"worldbank_filtered_{year_range[0]}_{year_range[1]}.csv",
            mime="text/csv",
        )
    with scol:
        st.write(
            f"**{len(df_explore):,}** satır · **{df_explore['Country'].nunique()}** "
            f"ülke · Yıllar **{year_range[0]}–{year_range[1]}**"
        )

# =========================================================================
# 9. GELECEĞİ TAHMİN ETME (FORM KULLANIMI)
# =========================================================================
# ÖNEMLİ KONU: Normalde Streamlit'te bir butona/slider'a tıkladığınız an tüm kod baştan çalışır.
# `st.form` ise birden fazla girdiyi gruplar. Kullanıcı tüm seçimleri yapıp 
# "st.form_submit_button"a basana kadar uygulama yeniden çalışmaz.
st.divider()
st.subheader("🔮 Hızlı Projeksiyon — Geleceğe Yönelik Tahmin Aracı")

with st.form("projector_form"):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        proj_country = st.selectbox(
            "Tahmin Yapılacak Ülke", country_options,
            index=country_options.index("Turkiye") if "Turkiye" in country_options else 0,
        )
    with c2:
        proj_metric = st.selectbox("Tahmin Edilecek Metrik", ["GDP", "Population", "GDP per capita"])
    with c3:
        proj_years = st.number_input(
            "Kaç Yıl İleri?", min_value=1, max_value=30, value=10, step=1,
        )
    # Formun çalışması için bir tetikleyici butona ihtiyaç vardır:
    submitted = st.form_submit_button("Tahmini Başlat", type="primary")

if submitted: # Eğer kullanıcı butona bastıysa:
    # Ülkenin son 10 yıllık verisini alıyoruz.
    hist = (panel[(panel["Country"] == proj_country)]
            .dropna(subset=[proj_metric])
            .sort_values("Year")
            .tail(10))

    if len(hist) < 2:
        st.warning(f"{proj_country} tahmini için yeterli geçmiş veri bulunamadı.")
    else:
        # Basit Bileşik Yıllık Büyüme Oranı (CAGR) Formülü: (Son Değer / İlk Değer) ^ (1 / Geçen Yıl) - 1
        first, last = hist[proj_metric].iloc[0], hist[proj_metric].iloc[-1]
        n = hist["Year"].iloc[-1] - hist["Year"].iloc[0]
        cagr = (last / first) ** (1 / n) - 1 if first > 0 else np.nan

        # Gelecekteki yılları (X ekseni) ve tahmin edilen değerleri (Y ekseni) matematiksel olarak üretiyoruz.
        future_years = np.arange(hist["Year"].iloc[-1] + 1,
                                 hist["Year"].iloc[-1] + 1 + proj_years)
        future_vals = last * (1 + cagr) ** np.arange(1, proj_years + 1)

        # `st.toast` ekranın sağ alt köşesinden çıkıp kaybolan ufak bilgilendirme (bildirim) kutucuklarıdır.
        st.toast(f"Son {n} yılın zımni büyüme oranı (CAGR): %{cagr*100:.1f}", icon="📈")

        # Geçmiş veri ile Gelecek veriyi aynı grafikte çizebilmek için birleştiriyoruz (concat).
        plot_df = pd.concat([
            hist[["Year", proj_metric]].assign(Type="Geçmiş Veri"),
            pd.DataFrame({"Year": future_years, proj_metric: future_vals,
                          "Type": "Gelecek Projeksiyonu"}),
        ])

        fig_proj = px.line(
            plot_df, x="Year", y=proj_metric, color="Type",
            markers=True, template="plotly_white",
            color_discrete_map={"Geçmiş Veri": "#1f77b4", "Gelecek Projeksiyonu": "#d62728"},
        )
        fig_proj.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_proj, use_container_width=True)

        # Tahmin edilen sonuca ait özet metrik kutusu.
        st.metric(
            f"{future_years[-1]} Yılı {proj_country} {proj_metric} Beklentisi",
            fmt_money(future_vals[-1]) if proj_metric != "Population" else fmt_int(future_vals[-1]),
            f"Her yıl ortalama %{cagr*100:+.1f} büyüme (CAGR) baz alınmıştır.",
        )

# =========================================================================
# 10. ALT BİLGİ (FOOTER)
# =========================================================================
st.divider()
st.caption(
    "Kaynak: Dünya Bankası Açık Verisi · Streamlit, Plotly ve Pandas ile geliştirilmiştir. "
    "Ülke bazlı tablo ve haritaların tutarlı çalışması için toplu bölgeler (örn. 'Dünya', 'OECD Üyeleri') "
    "varsayılan olarak analizlerin dışında bırakılmıştır."
)