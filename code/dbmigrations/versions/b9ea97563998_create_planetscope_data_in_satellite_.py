"""create planetscope data in satellite table

Revision ID: b9ea97563998
Revises: 4d0e5d67e0d7
Create Date: 2024-04-23 23:15:31.968553

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b9ea97563998"
down_revision = "4d0e5d67e0d7"
branch_labels = None
depends_on = None

satellite_table = "satellite"
indice_table = "indice"


def upgrade() -> None:
    # insert planetscope satellite
    op.execute(
        "INSERT INTO "
        + satellite_table
        + " (name, region_url, satellite, catalogue, cloud_cover) "
        "VALUES ('planetscope', 'https://services.sentinel-hub.com', 'S6', False, True)"
    )

    # insert indices related to planetscope
    ndwi_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'NDWI',
            '
                //NDWI

                var val = (green / 3000 - nir / 3000) / (green / 3000 + nir / 3000);

                return colorBlend(val,
                [-1, -0.5, -0.2, 0, 0.2, 0.5, 1.0],
                [
                    [1, 0, 1],
                    [1, 0.5, 0],
                    [1, 1, 0],
                    [0.2, 1, 0.5],
                    [0, 0, 1],
                    [0, 0, 0.3],
                    [0, 0, 0]
                ]);
            ', 
            'planetscope', 
            NULL, 
            'The NDWI is useful for water body mapping, as water bodies strongly absorb light in visible to infrared electromagnetic spectrum. NDWI uses green and near infrared bands to highlight water bodies. It is sensitive to built-up land and can result in over-estimation of water bodies.',
            'https://custom-scripts.sentinel-hub.com/planet_scope/ndwi/',
            'NDWI',
            NULL,
            'other',
            12
        )
    """

    ndvi_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'NDVI',
            '
                //NDVI
                var val = (nir - red) / (nir + red);

                return colorBlend(val,
                [0.0, 0.5, 1.0],
                [
                    [1, 0, 0],
                    [1, 1, 0],
                    [0.1, 0.31, 0],
                ]);
            ', 
            'planetscope', 
            NULL, 
            'The well known and widely used NDVI is a simple, but effective index for quantifying green vegetation. It normalizes green leaf scattering in Near Infra-red wavelengths with chlorophyll absorption in red wavelengths.',
            'https://custom-scripts.sentinel-hub.com/planet_scope/ndvi/',
            'NDVI',
            NULL,
            'All',
            12
        )
    """

    true_color_insert_query = """
        INSERT INTO indice (name, evalscript, satellite, statistical_evalscript, description, source, alias, legend, category, rank)
        VALUES (
            'True color',
            '
                //VERSION=3
                //True Color

                function setup() {
                return {
                    input: ["blue", "green", "red"],
                    output: { bands: 3 }
                };
                }

                function evaluatePixel(sample) {
                    return [sample.red / 3000, sample.green / 3000, sample.blue / 3000];
                }
            ', 
            'planetscope', 
            NULL, 
            'The true color product maps PlanetScope band values red, green, and blue which roughly correspond to red, green, and blue part of the spectrum, respectively, to R, G, and B components.',
            'https://custom-scripts.sentinel-hub.com/planet_scope/true_color/',
            'Latest Satellite Image',
            NULL,
            'other',
            15
        )
    """

    op.execute(ndwi_insert_query)
    op.execute(ndvi_insert_query)
    op.execute(true_color_insert_query)


def downgrade() -> None:

    # Remove indices related to planetscope
    op.execute(
        "DELETE FROM "
        + indice_table
        + " WHERE satellite = 'planetscope' AND name IN ('NDWI', 'True color')"
    )

    # Remove planetscope satellite record
    op.execute("DELETE FROM " + satellite_table + " WHERE name = 'planetscope'")
