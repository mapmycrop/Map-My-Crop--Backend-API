"""update indices table

Revision ID: 3b4a530a16b0
Revises: 7798e5f57a1d
Create Date: 2024-06-04 23:14:33.414086

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3b4a530a16b0"
down_revision = "7798e5f57a1d"
branch_labels = None
depends_on = None

indice_table = "indice"


def upgrade() -> None:
    fapar_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'FAPAR',
            '
                //VERSION=3 (auto-converted from 2)
                var degToRad = Math.PI / 180;

                function evaluatePixelOrig(samples) {
                var sample = samples[0];
                var b03_norm = normalize(sample.B03, 0, 0.253061520471542);
                var b04_norm = normalize(sample.B04, 0, 0.290393577911328);
                var b05_norm = normalize(sample.B05, 0, 0.305398915248555);
                var b06_norm = normalize(sample.B06, 0.006637972542253, 0.608900395797889);
                var b07_norm = normalize(sample.B07, 0.013972727018939, 0.753827384322927);
                var b8a_norm = normalize(sample.B8A, 0.026690138082061, 0.782011770669178);
                var b11_norm = normalize(sample.B11, 0.016388074192258, 0.493761397883092);
                var b12_norm = normalize(sample.B12, 0, 0.493025984460231);
                var viewZen_norm = normalize(Math.cos(sample.viewZenithMean * degToRad), 0.918595400582046, 1);
                var sunZen_norm  = normalize(Math.cos(sample.sunZenithAngles * degToRad), 0.342022871159208, 0.936206429175402);
                var relAzim_norm = Math.cos((sample.sunAzimuthAngles - sample.viewAzimuthMean) * degToRad)

                var n1 = neuron1(b03_norm,b04_norm,b05_norm,b06_norm,b07_norm,b8a_norm,b11_norm,b12_norm, viewZen_norm,sunZen_norm,relAzim_norm);
                var n2 = neuron2(b03_norm,b04_norm,b05_norm,b06_norm,b07_norm,b8a_norm,b11_norm,b12_norm, viewZen_norm,sunZen_norm,relAzim_norm);
                var n3 = neuron3(b03_norm,b04_norm,b05_norm,b06_norm,b07_norm,b8a_norm,b11_norm,b12_norm, viewZen_norm,sunZen_norm,relAzim_norm);
                var n4 = neuron4(b03_norm,b04_norm,b05_norm,b06_norm,b07_norm,b8a_norm,b11_norm,b12_norm, viewZen_norm,sunZen_norm,relAzim_norm);
                var n5 = neuron5(b03_norm,b04_norm,b05_norm,b06_norm,b07_norm,b8a_norm,b11_norm,b12_norm, viewZen_norm,sunZen_norm,relAzim_norm);
                
                var l2 = layer2(n1, n2, n3, n4, n5);
                
                var fapar = denormalize(l2, 0.000153013463222, 0.977135096979553);
                    return {
                        default: [fapar]
                    }
                }

                function neuron1(b03_norm,b04_norm,b05_norm,b06_norm,b07_norm,b8a_norm,b11_norm,b12_norm, viewZen_norm,sunZen_norm,relAzim_norm) {
                    var sum =
                        - 0.887068364040280
                        + 0.268714454733421 * b03_norm
                        - 0.205473108029835 * b04_norm
                        + 0.281765694196018 * b05_norm
                        + 1.337443412255980 * b06_norm
                        + 0.390319212938497 * b07_norm
                        - 3.612714342203350 * b8a_norm
                        + 0.222530960987244 * b11_norm
                        + 0.821790549667255 * b12_norm
                        - 0.093664567310731 * viewZen_norm
                        + 0.019290146147447 * sunZen_norm
                        + 0.037364446377188 * relAzim_norm;

                    return tansig(sum);
                }

                function neuron2(b03_norm,b04_norm,b05_norm,b06_norm,b07_norm,b8a_norm,b11_norm,b12_norm, viewZen_norm,sunZen_norm,relAzim_norm) {
                    var sum =
                        + 0.320126471197199
                        - 0.248998054599707 * b03_norm
                        - 0.571461305473124 * b04_norm
                        - 0.369957603466673 * b05_norm
                        + 0.246031694650909 * b06_norm
                        + 0.332536215252841 * b07_norm
                        + 0.438269896208887 * b8a_norm
                        + 0.819000551890450 * b11_norm
                        - 0.934931499059310 * b12_norm
                        + 0.082716247651866 * viewZen_norm
                        - 0.286978634108328 * sunZen_norm
                        - 0.035890968351662 * relAzim_norm;

                    return tansig(sum);
                }

                function neuron3(b03_norm,b04_norm,b05_norm,b06_norm,b07_norm,b8a_norm,b11_norm,b12_norm, viewZen_norm,sunZen_norm,relAzim_norm) {
                    var sum =
                        + 0.610523702500117
                        - 0.164063575315880 * b03_norm
                        - 0.126303285737763 * b04_norm
                        - 0.253670784366822 * b05_norm
                        - 0.321162835049381 * b06_norm
                        + 0.067082287973580 * b07_norm
                        + 2.029832288655260 * b8a_norm
                        - 0.023141228827722 * b11_norm
                        - 0.553176625657559 * b12_norm
                        + 0.059285451897783 * viewZen_norm
                        - 0.034334454541432 * sunZen_norm
                        - 0.031776704097009 * relAzim_norm;

                    return tansig(sum);
                }

                function neuron4(b03_norm,b04_norm,b05_norm,b06_norm,b07_norm,b8a_norm,b11_norm,b12_norm, viewZen_norm,sunZen_norm,relAzim_norm) {
                    var sum =
                        - 0.379156190833946
                        + 0.130240753003835 * b03_norm
                        + 0.236781035723321 * b04_norm
                        + 0.131811664093253 * b05_norm
                        - 0.250181799267664 * b06_norm
                        - 0.011364149953286 * b07_norm
                        - 1.857573214633520 * b8a_norm
                        - 0.146860751013916 * b11_norm
                        + 0.528008831372352 * b12_norm
                        - 0.046230769098303 * viewZen_norm
                        - 0.034509608392235 * sunZen_norm
                        + 0.031884395036004 * relAzim_norm;

                    return tansig(sum);
                }

                function neuron5(b03_norm,b04_norm,b05_norm,b06_norm,b07_norm,b8a_norm,b11_norm,b12_norm, viewZen_norm,sunZen_norm,relAzim_norm) {
                    var sum =
                        + 1.353023396690570
                        - 0.029929946166941 * b03_norm
                        + 0.795804414040809 * b04_norm
                        + 0.348025317624568 * b05_norm
                        + 0.943567007518504 * b06_norm
                        - 0.276341670431501 * b07_norm
                        - 2.946594180142590 * b8a_norm
                        + 0.289483073507500 * b11_norm
                        + 1.044006950440180 * b12_norm
                        - 0.000413031960419 * viewZen_norm
                        + 0.403331114840215 * sunZen_norm
                        + 0.068427130526696 * relAzim_norm;

                    return tansig(sum);
                }

                function layer2(neuron1, neuron2, neuron3, neuron4, neuron5) {
                    var sum =
                        - 0.336431283973339
                        + 2.126038811064490 * neuron1
                        - 0.632044932794919 * neuron2
                        + 5.598995787206250 * neuron3
                        + 1.770444140578970 * neuron4
                        - 0.267879583604849 * neuron5;

                    return sum;
                }

                function normalize(unnormalized, min, max) {
                    return 2 * (unnormalized - min) / (max - min) - 1;
                }
                function denormalize(normalized, min, max) {
                    return 0.5 * (normalized + 1) * (max - min) + min;
                }
                function tansig(input) {
                    return 2 / (1 + Math.exp(-2 * input)) - 1; 
                }

                function setup() {
                    return {
                        input: [{
                        bands: [
                            "B03",
                            "B04",
                            "B05",
                            "B06",
                            "B07",
                            "B8A",
                            "B11",
                            "B12",
                            "viewZenithMean",
                            "viewAzimuthMean",
                            "sunZenithAngles",
                            "sunAzimuthAngles"
                        ]
                        }],
                        output: [
                            {
                            id: "default",
                            sampleType: "AUTO",
                            bands: 1
                            }
                        ]
                    }
                }


                function evaluatePixel(sample, scene, metadata, customData, outputMetadata) {
                    const result = evaluatePixelOrig([sample], [scene], metadata, customData, outputMetadata);
                    return result[Object.keys(result)[0]];
                }
            ', 
            'sentinel-2-l2a', 
            NULL, 
            'FAPAR is the fraction of incoming solar radiation absorbed for photosynthesis by a photosynthetic organism (live leaves).',
            'https://custom-scripts.sentinel-hub.com/sentinel-2/fapar/',
            'FAPAR',
            NULL,
            'other',
            1
        )
    """

    ircei_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'IRECI',
            '
                //
                // Chlorophyll Red-Edge  (abbrv. Chlred-edge)
                //
                // General formula: (NIR/RE)-1
                //
                // doi: 10.1078/0176-1617-00887
                //

                let index = (B07 / B05) - 1;

                return colorBlend(index, [0, 1, 2.5, 5, 10, 20],
                [
                    [0, 0, 0],
                    [0, 0.5, 0],
                    [0.2, 0.8, 0],
                    [1, 1, 0],
                    [0.8, 0.8, 0.8],
                    [1, 1, 1]
                ]);
            ', 
            'sentinel-2-l2a', 
            NULL, 
            'Inverted Red-Edge Chlorophyll Index',
            'https://custom-scripts.sentinel-hub.com/sentinel-2/chl_rededge/',
            'IRECI',
            NULL,
            'other',
            2
        )
    """

    wiw_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'WIW',
            '
                // Detecting the Presence of Water in Wetlands with Sentinel-2 Satellite (abbrv. WIW)
                //
                // General formula: IF B8A<0.1804 AND B12<0.1131 THEN Water ELSE NoWater
                //
                // URL https://www.indexdatabase.de/db/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx//

                return B8A<0.1804&&B12<0.1131?[51/255,68/255,170/255]:[B04*5,B03*5,B02*5];

                // colorBlend will return a blue color when surface water is detected, and lighten to a natural color when no water is detected
            ', 
            'sentinel-2-l2a', 
            NULL, 
            'Water In Wetlands Index',
            'https://custom-scripts.sentinel-hub.com/sentinel-2/wiw_s2_script/',
            'WIW',
            NULL,
            'other',
            4
        )
    """

    ari1_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'ARI1',
            '
                // ARI1 - Anthocyanin Reflectance Index 1
                function setup() {
                    return {
                        input: ["B3", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let ari1 = 1 / scene[bands.index("B3")] - 1 / scene[bands.index("B4")];
                    return [ari1];
                }
            ', 
            'planetscope', 
            NULL, 
            'Anthocyanin Reflectance Index 1',
            '',
            'ARI1',
            NULL,
            'other',
            5
        )
    """

    car_re_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'CCI',
            '
                // CCI - Chlorophyll Carotenoid Index
                function setup() {
                    return {
                        input: ["B3", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let cci = (scene[bands.index("B4")] - scene[bands.index("B3")]) / (scene[bands.index("B4")] + scene[bands.index("B3")]);
                    return [cci];
                }
            ', 
            'planetscope', 
            NULL, 
            'Chlorophyll Carotenoid Index',
            '',
            'CCI',
            NULL,
            'other',
            6
        )
    """

    cl_re_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'CL_RE',
            '
                // CL_RE - Red-Edge Chlorophyll Index
                function setup() {
                    return {
                        input: ["B4", "B3"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let cl_re = (scene[bands.index("B4")] - scene[bands.index("B3")]) / (scene[bands.index("B4")] + scene[bands.index("B3")]);
                    return [cl_re];
                }
            ', 
            'planetscope', 
            NULL, 
            'Red-Edge Chlorophyll Index',
            '',
            'CL_RE',
            NULL,
            'other',
            7
        )
    """

    mtvi2_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'MTVI2',
            '
                // MTVI2 - Modified Triangular Vegetation Index - Improved
                function setup() {
                    return {
                        input: ["B2", "B3", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let l = 1.5;
                    let g = 2.5;
                    let nir = scene[bands.index("B4")];
                    let red = scene[bands.index("B3")];
                    let green = scene[bands.index("B2")];

                    let mtvi2 = 1.5 * (1.2 * (nir - green) - 2.5 * (red - green)) / Math.sqrt((2 * nir + 1) ** 2 - (6 * nir - 5 * Math.sqrt(red)) - 0.5);
                    return [mtvi2];
                }
            ', 
            'planetscope', 
            NULL, 
            'Modified Triangular Vegetation Index - Improved',
            '',
            'MTVI2',
            NULL,
            'other',
            8
        )
    """

    ndre_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'NDRE',
            '
                // NDRE - Normalized Difference Red Edge Index
                function setup() {
                    return {
                        input: ["B4", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let ndre = (scene[bands.index("B4")] - scene[bands.index("B4")]) / (scene[bands.index("B4")] + scene[bands.index("B4")]);
                    return [ndre];
                }
            ', 
            'planetscope', 
            NULL, 
            'Normalized Difference Red Edge Index',
            '',
            'NDRE',
            NULL,
            'other',
            9
        )
    """

    ndrex_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'NDREX',
            '
                // NDREX - Normalized Difference Red Edge Index
                function setup() {
                    return {
                        input: ["B4", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let ndrex = (scene[bands.index("B4")] - scene[bands.index("B4")]) / (scene[bands.index("B4")] + scene[bands.index("B4")]);
                    return [ndrex];
                }

            ', 
            'planetscope', 
            NULL, 
            'Normalized Difference Red Edge Index',
            '',
            'NDREX',
            NULL,
            'other',
            10
        )
    """

    pri_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'PRI',
            '
                // PRI - Photochemical Reflectance Index
                function setup() {
                    return {
                        input: ["B2", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let pri = (scene[bands.index("B4")] - scene[bands.index("B2")]) / (scene[bands.index("B4")] + scene[bands.index("B2")]);
                    return [pri];
                }
            ', 
            'planetscope', 
            NULL, 
            'Photochemical Reflectance Index',
            '',
            'PRI',
            NULL,
            'other',
            11
        )
    """

    pvi_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'PVI',
            '
                // PVI - Perpendicular Vegetation Index
                function setup() {
                    return {
                        input: ["B3", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let a = 1;
                    let b = 0;
                    let nir = scene[bands.index("B4")];
                    let red = scene[bands.index("B3")];
                    let pvi = (nir - a * red - b) / Math.sqrt(a ** 2 + 1);
                    return [pvi];
                }
            ', 
            'planetscope', 
            NULL, 
            'Perpendicular Vegetation Index',
            '',
            'PVI',
            NULL,
            'other',
            12
        )
    """

    si_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'SI',
            '
                // SI - Salinity Index
                function setup() {
                    return {
                        input: ["B1", "B2"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let si = (scene[bands.index("B1")] - scene[bands.index("B2")]) / (scene[bands.index("B1")] + scene[bands.index("B2")]);
                    return [si];
                }
            ', 
            'planetscope', 
            NULL, 
            'Salinity Index',
            '',
            'SI',
            NULL,
            'other',
            13
        )
    """

    sipi_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'SIPI',
            '
                // SIPI - Structure Insensitive Pigment Index
                function setup() {
                    return {
                        input: ["B1", "B3", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let sipi = (scene[bands.index("B4")] - scene[bands.index("B1")]) / (scene[bands.index("B4")] - scene[bands.index("B3")]);
                    return [sipi];
                }
            ', 
            'planetscope', 
            NULL, 
            'Structure Insensitive Pigment Index',
            '',
            'SIPI',
            NULL,
            'other',
            14
        )
    """

    soc_vis_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'SOC_VIS',
            '
                // SOC_VIS - Soil Organic Carbon (visible spectra)
                function setup() {
                    return {
                        input: ["B1", "B2", "B3"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let soc_vis = (scene[bands.index("B1")] - scene[bands.index("B2")]) / (scene[bands.index("B1")] + scene[bands.index("B2")]) * (scene[bands.index("B3")] / scene[bands.index("B2")]);
                    return [soc_vis];
                }
            ', 
            'planetscope', 
            NULL, 
            'Soil Organic Carbon (visible spectra)',
            '',
            'SOC_VIS',
            NULL,
            'other',
            15
        )
    """

    yrsi_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'YRSI',
            '
                // YRSI - Yellow Rust Spore Index
                function setup() {
                    return {
                        input: ["B1", "B2", "B3"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let yrsi = (scene[bands.index("B2")] - scene[bands.index("B3")]) / (scene[bands.index("B1")] + scene[bands.index("B2")]);
                    return [yrsi];
                }
            ', 
            'planetscope', 
            NULL, 
            'Yellow Rust Spore Index',
            '',
            'YRSI',
            NULL,
            'other',
            16
        )
    """

    evi_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'EVI',
            '
                // EVI - Enhanced Vegetation Index
                function setup() {
                    return {
                        input: ["B1", "B3", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let g = 2.5;
                    let c1 = 6;
                    let c2 = 7.5;
                    let nir = scene[bands.index("B4")];
                    let red = scene[bands.index("B3")];
                    let blue = scene[bands.index("B1")];

                    let evi = g * (nir - red) / (nir + c1 * red - c2 * blue + 1);
                    return [evi];
                }
            ', 
            'planetscope', 
            NULL, 
            'Enhanced Vegetation Index',
            '',
            'EVI',
            NULL,
            'other',
            17
        )
    """

    msavi2_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'MSAVI2',
            '
                // MSAVI2 - Modified Soil-adjusted Vegetation Index
                function setup() {
                    return {
                        input: ["B3", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let nir = scene[bands.index("B4")];
                    let red = scene[bands.index("B3")];
                    let msavi2 = (2 * nir + 1 - Math.sqrt((2 * nir + 1) ** 2 - 8 * (nir - red))) / 2;
                    return [msavi2];
                }
            ', 
            'planetscope', 
            NULL, 
            'Modified Soil-adjusted Vegetation Index',
            '',
            'MSAVI2',
            NULL,
            'other',
            18
        )
    """

    mndwi_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'MNDWI',
            '
                // MNDWI - Modified Normalized Difference Water Index (Sentinel-2)
                function setup() {
                    return {
                        input: ["B3", "B11"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let green = scene[bands.index("B3")];
                    let swir = scene[bands.index("B11")];
                    let mndwi = (green - swir) / (green + swir);
                    return [mndwi];
                }
            ', 
            'sentinel-2-l2a', 
            NULL, 
            'Modified Normalized Difference Water Index',
            '',
            'MNDWI',
            NULL,
            'other',
            19
        )
    """

    soc_vis_s2_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'SOC_VIS',
            '
                // SOC_VIS - Soil Organic Carbon (visible spectra) (Sentinel-2)
                function setup() {
                    return {
                        input: ["B2", "B3", "B4"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let blue = scene[bands.index("B2")];
                    let green = scene[bands.index("B3")];
                    let red = scene[bands.index("B4")];
                    let soc_vis = (blue - green) / (blue + green) * (red / green);
                    return [soc_vis];
                }
            ', 
            'sentinel-2-l2a', 
            NULL, 
            'Soil Organic Carbon (visible spectra)',
            '',
            'SOC_VIS',
            NULL,
            'other',
            20
        )
    """

    ndrex_s2_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'NDREX',
            '
                // NDREX - Normalized Difference Red Edge Index (B04, B09) (Sentinel-2)
                function setup() {
                    return {
                        input: ["B4", "B09"],
                        output: { bands: 1 }
                    };
                }

                function evalscript(scene, bands) {
                    let red_edge = scene[bands.index("B09")];
                    let nir = scene[bands.index("B4")];
                    let ndrex = (nir - red_edge) / (nir + red_edge);
                    return [ndrex];
                }
            ', 
            'sentinel-2-l2a', 
            NULL, 
            'Normalized Difference Red Edge Index (B04, B09)',
            '',
            'NDREX',
            NULL,
            'other',
            21
        )
    """

    op.execute(fapar_insert_query)
    op.execute(ircei_insert_query)
    op.execute(wiw_insert_query)
    op.execute(ari1_insert_query)
    op.execute(car_re_insert_query)
    op.execute(cl_re_insert_query)
    op.execute(mtvi2_insert_query)
    op.execute(ndre_insert_query)
    op.execute(ndrex_insert_query)
    op.execute(pri_insert_query)
    op.execute(pvi_insert_query)
    op.execute(si_insert_query)
    op.execute(sipi_insert_query)
    op.execute(soc_vis_insert_query)
    op.execute(yrsi_insert_query)
    op.execute(evi_insert_query)
    op.execute(msavi2_insert_query)
    op.execute(mndwi_insert_query)
    op.execute(soc_vis_s2_insert_query)
    op.execute(ndrex_s2_insert_query)


def downgrade() -> None:
    op.execute(
        "DELETE FROM "
        + indice_table
        + " WHERE satellite = 'planetscope' AND name IN ("
        + "'CAR_RE', 'CCI', 'CL_RE', 'MTVI2', 'NDRE', 'NDREX', 'PRI', 'PVI', 'SI', 'SIPI', 'SOC_VIS', 'YRSI', 'EVI', 'MSAVI2', 'ARI1'"
        + ")"
    )

    op.execute(
        "DELETE FROM "
        + indice_table
        + " WHERE satellite = 'sentinel-2-l2a' AND name IN ("
        + "'FAPAR', 'IRECI', 'WIW', 'MNDWI', 'SOC_VIS', 'NDREX'"
        + ")"
    )
