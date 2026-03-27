#!/usr/bin/env python3
"""Convert IFC model to GLB (binary glTF) for Three.js web viewer."""

import ifcopenshell
import ifcopenshell.geom
import numpy as np
import struct
import json
import os

def ifc_to_glb(ifc_path, glb_path):
    model = ifcopenshell.open(ifc_path)

    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    settings.set("weld-vertices", True)

    # Collect all meshes
    meshes = []
    iterator = ifcopenshell.geom.iterator(settings, model)

    if iterator.initialize():
        while True:
            shape = iterator.get()
            element = model.by_id(shape.id)

            geo = shape.geometry
            verts = geo.verts       # flat list: x0,y0,z0, x1,y1,z1, ...
            faces = geo.faces       # flat list: i0,i1,i2, ...
            materials = geo.materials
            material_ids = geo.material_ids

            if len(verts) == 0 or len(faces) == 0:
                if not iterator.next():
                    break
                continue

            # Get colour from first material or style
            r, g, b, a = 0.7, 0.7, 0.7, 1.0
            if materials:
                mat = materials[0]
                try:
                    d = mat.diffuse
                    if d is not None:
                        r, g, b = float(d.r), float(d.g), float(d.b)
                    if mat.has_transparency:
                        a = 1.0 - float(mat.transparency)
                except Exception:
                    pass

            # Convert to numpy arrays
            verts_arr = np.array(verts, dtype=np.float32).reshape(-1, 3)
            faces_arr = np.array(faces, dtype=np.uint32).reshape(-1, 3)

            meshes.append({
                'name': element.Name or element.is_a(),
                'ifc_type': element.is_a(),
                'vertices': verts_arr,
                'indices': faces_arr.flatten(),
                'color': [r, g, b, a],
            })

            if not iterator.next():
                break

    if not meshes:
        print("No geometry found in IFC file!")
        return

    print(f"Extracted {len(meshes)} meshes from IFC")

    # Build glTF structure
    gltf = {
        "asset": {"version": "2.0", "generator": "SJ-BIM-Generator"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(meshes)))}],
        "nodes": [],
        "meshes": [],
        "accessors": [],
        "bufferViews": [],
        "buffers": [],
        "materials": [],
    }

    buffer_data = bytearray()

    for i, mesh_data in enumerate(meshes):
        verts = mesh_data['vertices']
        indices = mesh_data['indices'].astype(np.uint32)
        r, g, b, a = mesh_data['color']

        # Material
        mat_idx = len(gltf['materials'])
        mat = {
            "pbrMetallicRoughness": {
                "baseColorFactor": [float(r), float(g), float(b), float(a)],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.7,
            },
            "name": mesh_data['name'],
        }
        if a < 0.99:
            mat["alphaMode"] = "BLEND"
        gltf['materials'].append(mat)

        # Vertex buffer
        vert_bytes = verts.tobytes()
        vert_offset = len(buffer_data)
        buffer_data.extend(vert_bytes)
        # Pad to 4-byte boundary
        while len(buffer_data) % 4:
            buffer_data.append(0)

        # Index buffer
        idx_bytes = indices.tobytes()
        idx_offset = len(buffer_data)
        buffer_data.extend(idx_bytes)
        while len(buffer_data) % 4:
            buffer_data.append(0)

        # Compute bounds
        v_min = verts.min(axis=0).tolist()
        v_max = verts.max(axis=0).tolist()

        # BufferViews
        vert_bv = len(gltf['bufferViews'])
        gltf['bufferViews'].append({
            "buffer": 0,
            "byteOffset": vert_offset,
            "byteLength": len(vert_bytes),
            "target": 34962,  # ARRAY_BUFFER
            "byteStride": 12,
        })

        idx_bv = len(gltf['bufferViews'])
        gltf['bufferViews'].append({
            "buffer": 0,
            "byteOffset": idx_offset,
            "byteLength": len(idx_bytes),
            "target": 34963,  # ELEMENT_ARRAY_BUFFER
        })

        # Accessors
        vert_acc = len(gltf['accessors'])
        gltf['accessors'].append({
            "bufferView": vert_bv,
            "componentType": 5126,  # FLOAT
            "count": len(verts),
            "type": "VEC3",
            "min": v_min,
            "max": v_max,
        })

        idx_acc = len(gltf['accessors'])
        gltf['accessors'].append({
            "bufferView": idx_bv,
            "componentType": 5125,  # UNSIGNED_INT
            "count": len(indices),
            "type": "SCALAR",
            "min": [int(indices.min())],
            "max": [int(indices.max())],
        })

        # Mesh
        gltf['meshes'].append({
            "name": mesh_data['name'],
            "primitives": [{
                "attributes": {"POSITION": vert_acc},
                "indices": idx_acc,
                "material": mat_idx,
            }],
        })

        # Node
        gltf['nodes'].append({
            "mesh": i,
            "name": mesh_data['name'],
            "extras": {"ifc_type": mesh_data['ifc_type']},
        })

    # Buffer
    gltf['buffers'].append({"byteLength": len(buffer_data)})

    # Write binary GLB
    gltf_json = json.dumps(gltf, separators=(',', ':')).encode('utf-8')
    # Pad JSON to 4-byte alignment
    while len(gltf_json) % 4:
        gltf_json += b' '

    # GLB header: magic, version, length
    total_length = 12 + 8 + len(gltf_json) + 8 + len(buffer_data)

    with open(glb_path, 'wb') as f:
        # Header
        f.write(struct.pack('<I', 0x46546C67))  # glTF magic
        f.write(struct.pack('<I', 2))             # version
        f.write(struct.pack('<I', total_length))  # total length

        # JSON chunk
        f.write(struct.pack('<I', len(gltf_json)))  # chunk length
        f.write(struct.pack('<I', 0x4E4F534A))       # JSON magic
        f.write(gltf_json)

        # Binary chunk
        f.write(struct.pack('<I', len(buffer_data)))  # chunk length
        f.write(struct.pack('<I', 0x004E4942))         # BIN magic
        f.write(buffer_data)

    file_size = os.path.getsize(glb_path)
    print(f"GLB written to {glb_path} ({file_size:,} bytes, {len(meshes)} meshes)")


if __name__ == "__main__":
    ifc_to_glb("web/static/model.ifc", "web/static/model.glb")
