"use client";

import { useEffect, useRef } from "react";
import type { Map as LeafletMap, Marker } from "leaflet";
import type { Field } from "@/lib/types";
import { getHealthColor } from "@/lib/utils";

interface Props {
  fields: Field[];
  selectedFieldId: string | null;
  onFieldSelect: (id: string) => void;
}

export default function FarmMapLeaflet({ fields, selectedFieldId, onFieldSelect }: Props) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<LeafletMap | null>(null);
  const markersRef = useRef<Marker[]>([]);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Dynamic import to avoid SSR
    import("leaflet").then((L) => {
      // Fix default icon paths for Next.js
      delete (L.Icon.Default.prototype as { _getIconUrl?: unknown })._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
        iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
      });

      const center: [number, number] = [30.7333, 76.7800];
      const map = L.map(mapRef.current!, {
        center,
        zoom: 14,
        zoomControl: true,
        scrollWheelZoom: true,
      });

      // Dark satellite-style tile layer
      L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        {
          attribution: '&copy; <a href="https://carto.com">CARTO</a>',
          subdomains: "abcd",
          maxZoom: 19,
        }
      ).addTo(map);

      mapInstanceRef.current = map;

      // Add field polygons and markers
      fields.forEach((field) => {
        const [lat, lng] = field.coordinates;
        const color = getHealthColor(field.health_score);

        // Create a rough polygon around the field centre
        const offset = field.area_hectares * 0.0008;
        const bounds: [number, number][] = [
          [lat - offset, lng - offset],
          [lat - offset, lng + offset * 1.5],
          [lat + offset * 1.2, lng + offset * 1.5],
          [lat + offset * 1.2, lng - offset],
        ];

        const polygon = L.polygon(bounds, {
          color,
          fillColor: color,
          fillOpacity: 0.15,
          weight: 2,
          dashArray: field.status === "critical" ? "6 4" : undefined,
        }).addTo(map);

        polygon.bindPopup(`
          <div style="font-family: Inter, sans-serif; min-width: 160px;">
            <div style="font-weight: 700; font-size: 13px; margin-bottom: 4px;">${field.name}</div>
            <div style="font-size: 11px; color: #888; margin-bottom: 8px;">${field.crop} · ${field.growth_stage}</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
              <div><span style="color:#888;font-size:10px">Moisture</span><br><b>${field.latest_reading.soil_moisture.toFixed(1)}%</b></div>
              <div><span style="color:#888;font-size:10px">Temp</span><br><b>${field.latest_reading.temperature.toFixed(1)}°C</b></div>
              <div><span style="color:#888;font-size:10px">Health</span><br><b style="color:${color}">${field.health_score}/100</b></div>
              <div><span style="color:#888;font-size:10px">Area</span><br><b>${field.area_hectares} ha</b></div>
            </div>
          </div>
        `, { className: "agri-popup" });

        // Sensor node markers
        field.devices.forEach((device, di) => {
          const deviceLat = lat + (di % 2 === 0 ? offset * 0.4 : -offset * 0.3);
          const deviceLng = lng + (di % 2 === 0 ? offset * 0.5 : offset * 0.8);
          const nodeColor = device.status === "online" ? "#22c55e" : device.status === "warning" ? "#f59e0b" : "#ef4444";

          const nodeIcon = L.divIcon({
            className: "",
            html: `<div style="
              width:12px; height:12px; border-radius:50%;
              background:${nodeColor};
              border:2px solid #0a0f0d;
              box-shadow:0 0 8px ${nodeColor};
            "></div>`,
            iconSize: [12, 12],
            iconAnchor: [6, 6],
          });

          const marker = L.marker([deviceLat, deviceLng], { icon: nodeIcon }).addTo(map);
          marker.bindTooltip(`${device.name} · ${device.status} · 🔋${device.battery}%`, {
            direction: "top", offset: [0, -6],
          });
          markersRef.current.push(marker);
        });

        // Field label
        L.marker([lat, lng], {
          icon: L.divIcon({
            className: "",
            html: `<div style="
              background:rgba(10,15,13,0.85);
              border:1px solid ${color}40;
              color:${color};
              padding:3px 7px;
              border-radius:6px;
              font-size:10px;
              font-weight:600;
              font-family:Inter,sans-serif;
              white-space:nowrap;
            ">${field.name}</div>`,
            iconAnchor: [40, 10],
          }),
        }).addTo(map);

        polygon.on("click", () => onFieldSelect(field.id));
      });
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      <style>{`
        .agri-popup .leaflet-popup-content-wrapper {
          background: #141f18;
          border: 1px solid #1f3028;
          border-radius: 10px;
          color: #e8f5e9;
          box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }
        .agri-popup .leaflet-popup-tip {
          background: #141f18;
        }
        .leaflet-control-zoom a {
          background: #141f18 !important;
          border-color: #1f3028 !important;
          color: #86a98f !important;
        }
        .leaflet-control-zoom a:hover {
          background: #1a2820 !important;
          color: #4ade80 !important;
        }
        .leaflet-control-attribution {
          background: rgba(10,15,13,0.8) !important;
          color: #4a6450 !important;
          font-size: 9px;
        }
        .leaflet-control-attribution a { color: #4a6450 !important; }
      `}</style>
      <link
        rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"
      />
      <div
        ref={mapRef}
        style={{
          height: "520px",
          borderRadius: "14px",
          overflow: "hidden",
          border: "1px solid var(--bg-border)",
        }}
      />
    </>
  );
}
