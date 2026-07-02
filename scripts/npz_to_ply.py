#!/usr/bin/env python3
import argparse
import numpy as np
from plyfile import PlyData, PlyElement
import os

def npz_to_ply_fixed(npz_path, ply_path):
    print(f"Loading {npz_path}...")
    data = np.load(npz_path)
    means3D = data['means3D']
    
    # SplaTAM rgb_colors are raw RGB [0,1]. WebGL viewers expect f_dc (SH0).
    # RGB = f_dc * 0.28209479177387814 + 0.5
    # Therefore: f_dc = (RGB - 0.5) / 0.28209479177387814
    C0 = 0.28209479177387814
    raw_rgb = data['rgb_colors']
    f_dc = (raw_rgb - 0.5) / C0
    
    opacities = data['logit_opacities']
    scales = data['log_scales']
    
    unnorm_rots = data['unnorm_rotations']
    norms = np.linalg.norm(unnorm_rots, axis=1, keepdims=True)
    rots = unnorm_rots / (norms + 1e-8)
    
    dtype_full = [(attribute, 'f4') for attribute in ['x', 'y', 'z', 'nx', 'ny', 'nz', 'f_dc_0', 'f_dc_1', 'f_dc_2', 'opacity', 'scale_0', 'scale_1', 'scale_2', 'rot_0', 'rot_1', 'rot_2', 'rot_3']]
    
    elements = np.empty(means3D.shape[0], dtype=dtype_full)
    
    elements['x'] = means3D[:, 0]
    elements['y'] = means3D[:, 1]
    elements['z'] = means3D[:, 2]
    elements['nx'] = 0
    elements['ny'] = 0
    elements['nz'] = 0
    elements['f_dc_0'] = f_dc[:, 0]
    elements['f_dc_1'] = f_dc[:, 1]
    elements['f_dc_2'] = f_dc[:, 2]
    elements['opacity'] = opacities[:, 0]
    elements['scale_0'] = scales[:, 0]
    elements['scale_1'] = scales[:, 1]
    elements['scale_2'] = scales[:, 2]
    elements['rot_0'] = rots[:, 0]
    elements['rot_1'] = rots[:, 1]
    elements['rot_2'] = rots[:, 2]
    elements['rot_3'] = rots[:, 3]
    
    print(f"Writing {means3D.shape[0]} Gaussians to {ply_path}...")
    el = PlyElement.describe(elements, 'vertex')
    PlyData([el], text=False).write(ply_path)
    print("Done! You can now drag this .ply file into SuperSplat or other WebGL viewers.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert SplaTAM params.npz to WebGL-compatible .ply")
    parser.add_argument('--input', type=str, required=True, help="Path to input params.npz")
    parser.add_argument('--output', type=str, default=None, help="Path to output .ply (optional)")
    args = parser.parse_args()
    
    out_path = args.output
    if out_path is None:
        out_path = os.path.splitext(args.input)[0] + ".ply"
        
    npz_to_ply_fixed(args.input, out_path)
