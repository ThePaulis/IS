"use client"

import React, { useEffect, useRef, useState } from 'react';
import { LayerGroup, LayersControl, MapContainer, Marker, TileLayer, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet-defaulticon-compatibility";
import { Warehouse } from '../interface';
import L from 'leaflet';
import Supercluster from 'supercluster';
import { toast } from 'react-toastify';
import WarehouseDetailsDialog from './WarehouseDetailsDialog';

const LeafleatMap = ({ warehouses, updatePoint } : { warehouses: Warehouse[], updatePoint: (id: number, latitude: number, longitude: number) => any }) => {
    const [clusters, setClusters]   = useState<any[]>([])
    const mapRef                    = useRef<any>(null)
    const warehouseDetailsDialogRef = useRef<any>(null)

    const superclusterRef = useRef(
        new Supercluster({
            radius: 40, // Cluster radius in pixels
            maxZoom: 20, // Max zoom for clustering
        })
    )
      
    const updateClusters = (map: { getBounds: () => any; getZoom: () => any; }) => {
        const bounds    = map.getBounds();
        const zoom      = map.getZoom();
    
        const bbox: any = [
            bounds.getWest(),
            bounds.getSouth(),
            bounds.getEast(),
            bounds.getNorth(),
        ];
    
        const clusters: any = superclusterRef.current.getClusters(bbox, zoom)

        setClusters(clusters)

        return
    }
    
    useEffect(() => {
        const geoJSONPlaces = warehouses.map(place => {
            const geoJSONPlace: any = {
                type: "Feature",
                properties: {
                    id: place.id,
                    name: place.name,
                    latitude: place.latitude,
                    longitude: place.longitude
                },
                geometry: {
                    type: "Point",
                    coordinates: [place.longitude, place.latitude]
                }
            }
    
            return geoJSONPlace
        })

        superclusterRef.current.load(geoJSONPlaces); // Load points into supercluster

        if(!mapRef.current) {
            setTimeout(() => {
                const mapInstance = mapRef.current;
                updateClusters(mapInstance)
            }, 100)
        }

        if (mapRef.current) {
            const mapInstance = mapRef.current;
            updateClusters(mapInstance)
        }
    }, [warehouses])

    const MapEvents = () => {
        const map = useMap()

        map.on("moveend", () => updateClusters(map))
        
        return null
    }

    const onHandleDragMarkerOver = async (e: any, id: number) => {
        const _lat = e.target._latlng.lat
        const _lng = e.target._latlng.lng

        const promise_update = await updatePoint(id, _lat, _lng)

        if(promise_update.status){
            console.error(promise_update)
            toast.error('Error saving data.')
            return
        }

        const idx = clusters.findIndex((cluster: { properties: {id: number | string} }) => String(cluster.properties.id) === String(id))

        if(idx > -1){
            const new_clusters: any[] = [...clusters]

            new_clusters[idx].properties = {
                ...new_clusters[idx].properties,
                latitude: _lat,
                longitude: _lng
            }

            new_clusters[idx].geometry = {
                ...new_clusters[idx].geometry,
                coordinates: [_lng, _lat]
            }

            setClusters(new_clusters)
        }
    }

    const onMarkerClick = (warehouse: any) => {
        if (warehouseDetailsDialogRef.current) {
            warehouseDetailsDialogRef.current.handleClickOpen(warehouse);
        }
    }

    return (
        <>
            <MapContainer
                center={[0, 0]}
                zoom={3}
                scrollWheelZoom={true}
                style={{ height: "100%", width: "100%" }}
                className='relative'
                ref={mapRef}
            >
                <LayersControl position="topright">
                    {/* Base Layers */}
                    <LayersControl.BaseLayer checked name="OpenStreetMap">
                        <TileLayer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        />
                    </LayersControl.BaseLayer>

                    <LayersControl.BaseLayer name="CartoDB Positron">
                        <TileLayer
                            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                            attribution='&copy; <a href="https://www.carto.com/">CARTO</a>'
                        />
                    </LayersControl.BaseLayer>

                    <LayersControl.BaseLayer name="Dark Map">
                        <TileLayer
                            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                            attribution='&copy; <a href="https://www.carto.com/">CARTO</a>'
                        />
                    </LayersControl.BaseLayer>
                
                    <LayersControl.Overlay checked name="Warehouses">
                        <LayerGroup>
                            {clusters.map((cluster: any) => {
                                const [longitude, latitude] = cluster.geometry.coordinates;
                                const { cluster: isCluster, point_count: pointCount } = cluster.properties;

                                if (isCluster) {
                                    return (
                                        <Marker
                                        key={`cluster-${cluster.id}`}
                                        position={[latitude, longitude]}
                                        icon={L.divIcon({
                                            html: `<div style="background-color:rgba(0, 123, 255, 0.8); color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;">
                                                ${pointCount}
                                            </div>`,
                                            className: "cluster-marker",
                                            iconSize: [30, 30],
                                        })}
                                        />
                                    );
                                }

                                return (
                                    <Marker
                                        key={`marker-${cluster.properties.id}`}
                                        position={[latitude, longitude]}
                                        draggable={true}
                                        eventHandlers={{
                                            dragend: (e) => onHandleDragMarkerOver(e, cluster.properties.id),
                                            click: () => onMarkerClick(cluster.properties),
                                        }}
                                    />
                                );
                        })}
                    </LayerGroup>
                </LayersControl.Overlay>
            </LayersControl>
                
            <MapEvents />
        </MapContainer>
        <WarehouseDetailsDialog ref={warehouseDetailsDialogRef} />
        </>
    );
};

export default LeafleatMap;
