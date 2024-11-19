<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" indent="yes"/>
    <xsl:template match="/data">
        <data>
            <xsl:for-each select="row[country[country_name='Brazil']]">
                <row>
                    <id><xsl:value-of select="id"/></id>
                    <name><xsl:value-of select="name"/></name>
                    <state>
                        <state_id><xsl:value-of select="state/state_id"/></state_id>
                        <state_code><xsl:value-of select="state/state_code"/></state_code>
                        <state_name><xsl:value-of select="state/state_name"/></state_name>
                    </state>
                    <country>
                        <country_id><xsl:value-of select="country/country_id"/></country_id>
                        <country_code><xsl:value-of select="country/country_code"/></country_code>
                        <country_name><xsl:value-of select="country/country_name"/></country_name>
                    </country>
                    <latitude><xsl:value-of select="latitude"/></latitude>
                    <longitude><xsl:value-of select="longitude"/></longitude>
                    <wikiDataId><xsl:value-of select="wikiDataId"/></wikiDataId>
                </row>
            </xsl:for-each>
        </data>
    </xsl:template>
</xsl:stylesheet>