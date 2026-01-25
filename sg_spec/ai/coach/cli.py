"""
Smart Guitar Coach CLI.

Commands:
- sgc export-bundle: Build firmware envelope from evaluation + assignment
- sgc ota-pack: Build OTA payload with HMAC signature
- sgc ota-verify: Verify HMAC-signed OTA payload
- sgc ota-bundle: Build OTA folder/zip bundle from SessionRecord
- sgc ota-verify-zip: Verify bundle.zip integrity
- sgc dance-pack-set-list: List bundled dance pack sets
- sgc dance-pack-set-validate: Validate pack set references
- sgc dance-pack-set-show: Show pack set summary
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import zipfile
from pathlib import Path

from .schemas import ProgramRef, ProgramType, SessionRecord
from .coach_policy import evaluate_session
from .assignment_policy import plan_assignment
from .assignment_serializer import serialize_bundle
from .ota_payload import (
    build_ota_payload,
    verify_ota_payload,
    build_assignment_ota_bundle,
    verify_bundle_integrity,
    verify_zip_bundle,
)
# Dance Pack imports
from .dance_pack import load_pack_by_id, pack_to_assignment_defaults, list_pack_ids
from .dance_pack_set import (
    DancePackSetV1,
    load_set_by_id,
    load_set_from_file,
    list_all_sets,
    validate_set_references,
)
from .pack_set_policy import (
    get_pack_defaults_from_set,
    get_pack_defaults_from_set_id,
    summarize_pack_set,
)



def _read_text(path: str | Path) -> str:
    """Read text from a file, raising FileNotFoundError if missing."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return p.read_text(encoding="utf-8")


def _read_json(path: str | Path) -> dict:
    """Read JSON from a file."""
    return json.loads(_read_text(path))


def _find_bundle_root(extract_dir: Path) -> Path:
    """
    Find the directory containing manifest.json.
    
    Supports:
      - zip with files at root
      - zip with a single top-level folder
    """
    if (extract_dir / "manifest.json").exists():
        return extract_dir

    matches = list(extract_dir.rglob("manifest.json"))
    if not matches:
        raise ValueError("manifest.json not found in zip")
    if len(matches) > 1:
        raise ValueError("multiple manifest.json found in zip (ambiguous)")
    return matches[0].parent


# ============================================================================
# Commands: Export Bundle (JSON envelope)
# ============================================================================


def cmd_export_bundle(args: argparse.Namespace) -> int:
    """
    Build firmware envelope from session -> evaluation -> assignment.
    Outputs JSON to stdout or file.
    """
    session_json = _read_text(args.session)
    session = SessionRecord.model_validate_json(session_json)

    ev = evaluate_session(session)

    # Build program ref (use session's program if available)
    program = session.program_ref

    assignment = plan_assignment(ev, program)
    bundle = serialize_bundle(assignment)

    output = json.dumps(bundle, indent=2, sort_keys=True)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(output)

    return 0


# ============================================================================
# Commands: OTA Pack (HMAC signed JSON)
# ============================================================================


def cmd_ota_pack(args: argparse.Namespace) -> int:
    """
    Build HMAC-signed OTA payload from session.
    """
    session_json = _read_text(args.session)
    session = SessionRecord.model_validate_json(session_json)

    ev = evaluate_session(session)
    program = session.program_ref
    assignment = plan_assignment(ev, program)

    # Read secret if provided
    secret = None
    if args.secret:
        secret = args.secret.encode("utf-8")
    elif args.secret_file:
        secret = Path(args.secret_file).read_bytes().strip()

    payload = build_ota_payload(assignment, secret=secret)

    output = json.dumps(payload, indent=2, sort_keys=True)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(output)

    return 0


def cmd_ota_verify_hmac(args: argparse.Namespace) -> int:
    """
    Verify HMAC signature of OTA payload.
    """
    payload_json = _read_text(args.payload)
    payload = json.loads(payload_json)

    # Read secret
    if args.secret:
        secret = args.secret.encode("utf-8")
    elif args.secret_file:
        secret = Path(args.secret_file).read_bytes().strip()
    else:
        print("ERROR: --secret or --secret-file required", file=sys.stderr)
        return 1

    if verify_ota_payload(payload, secret=secret):
        print("OK: signature valid")
        return 0
    else:
        print("FAIL: signature invalid or missing")
        return 1


# ============================================================================
# Commands: OTA Bundle (folder/zip)
# ============================================================================


def cmd_ota_bundle(args: argparse.Namespace) -> int:
    """
    Build an OTA bundle folder/zip from a SessionRecord JSON.
    Mode 1 pipeline: SessionRecord -> CoachEvaluation -> PracticeAssignment -> OTA bundle.
    """
    session_json = _read_text(args.session)
    session = SessionRecord.model_validate_json(session_json)

    ev = evaluate_session(session)
    program = session.program_ref
    assignment = plan_assignment(ev, program)

    make_zip = bool(args.zip)

    # HMAC secret if provided
    hmac_secret = None
    if args.secret:
        hmac_secret = args.secret.encode("utf-8")
    elif args.secret_file:
        hmac_secret = Path(args.secret_file).read_bytes().strip()

    res = build_assignment_ota_bundle(
        assignment=assignment,
        out_dir=args.out,
        bundle_name=args.name,
        product=args.product,
        target_device_model=args.device_model,
        target_min_firmware=args.min_firmware,
        attachments=None,
        make_zip=make_zip,
        hmac_secret=hmac_secret,
    )

    print(str(res.bundle_dir))
    if res.zip_path is not None:
        print(str(res.zip_path))

    return 0


def cmd_ota_verify_folder(args: argparse.Namespace) -> int:
    """
    Verify an OTA bundle directory (folder form).
    """
    bundle_dir = Path(args.bundle_dir)

    if not verify_bundle_integrity(bundle_dir):
        print("FAIL: bundle integrity check failed")
        return 1

    print("OK")
    return 0


def cmd_ota_verify_zip(args: argparse.Namespace) -> int:
    """
    Verify a bundle.zip by extracting to a temp dir and verifying.
    """
    zip_path = Path(args.zip_path)

    # Read secret if provided
    secret = None
    if args.secret:
        secret = args.secret.encode("utf-8")
    elif args.secret_file:
        secret = Path(args.secret_file).read_bytes().strip()

    success, error = verify_zip_bundle(zip_path, secret=secret)

    if success:
        print("OK")
        return 0
    else:
        print(f"FAIL: {error}")
        return 1




# ============================================================================
# Commands: Dance Pack Sets
# ============================================================================


def cmd_dance_pack_set_list(args: argparse.Namespace) -> int:
    """
    List all bundled dance pack sets.
    """
    sets = list_all_sets()
    
    if args.json:
        data = [
            {
                "id": s.id,
                "display_name": s.display_name,
                "tier": s.tier,
                "pack_count": len(s.packs),
            }
            for s in sets
        ]
        print(json.dumps(data, indent=2))
    else:
        for s in sets:
            print(f"{s.id}  ({s.tier})  {s.display_name}  [{len(s.packs)} packs]")
    
    return 0


def cmd_dance_pack_set_validate(args: argparse.Namespace) -> int:
    """
    Validate a pack set (bundled or from file).
    Checks that all referenced pack IDs exist.
    """
    try:
        if args.path:
            pack_set = load_set_from_file(args.path)
        else:
            pack_set = load_set_by_id(args.set_id)
        
        validate_set_references(pack_set)
        
        if not args.quiet:
            print(f"OK: {pack_set.id} ({len(pack_set.packs)} packs)")
            for pid in pack_set.packs:
                print(f"  - {pid}")
        
        return 0
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2


def cmd_dance_pack_set_show(args: argparse.Namespace) -> int:
    """
    Show detailed summary of a pack set.
    """
    try:
        summary = summarize_pack_set(args.set_id)
        
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Set: {summary['display_name']} ({summary['id']})")
            print(f"Tier: {summary['tier']}")
            print(f"Tags: {', '.join(summary['tags']) if summary['tags'] else '(none)'}")
            print(f"Packs ({summary['pack_count']}):")
            for p in summary['packs']:
                print(f"  - {p['pack_id']}: {p['display_name']}")
                print(f"      {p['difficulty']} | {p['tempo_range']} | {p['subdivision']}")
        
        return 0
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


def cmd_dance_pack_list(args: argparse.Namespace) -> int:
    """
    List all bundled dance packs.
    """
    pack_ids = list_pack_ids()
    
    if args.json:
        print(json.dumps(pack_ids, indent=2))
    else:
        for pid in pack_ids:
            print(pid)
    
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    p = argparse.ArgumentParser(
        prog="sgc",
        description="Smart Guitar Coach CLI (Mode 1 / OTA tools)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # --- export-bundle ---
    p_e = sub.add_parser("export-bundle", help="Build firmware envelope JSON from SessionRecord.")
    p_e.add_argument("--session", required=True, help="Path to session.json (SessionRecord).")
    p_e.add_argument("--output", "-o", default=None, help="Output file (stdout if omitted).")
    p_e.set_defaults(func=cmd_export_bundle)

    # --- ota-pack ---
    p_p = sub.add_parser("ota-pack", help="Build HMAC-signed OTA payload JSON.")
    p_p.add_argument("--session", required=True, help="Path to session.json (SessionRecord).")
    p_p.add_argument("--secret", default=None, help="HMAC secret string.")
    p_p.add_argument("--secret-file", default=None, help="Path to file containing HMAC secret.")
    p_p.add_argument("--output", "-o", default=None, help="Output file (stdout if omitted).")
    p_p.set_defaults(func=cmd_ota_pack)

    # --- ota-verify (HMAC) ---
    p_vh = sub.add_parser("ota-verify", help="Verify HMAC signature of OTA payload JSON.")
    p_vh.add_argument("payload", help="Path to OTA payload JSON file.")
    p_vh.add_argument("--secret", default=None, help="HMAC secret string.")
    p_vh.add_argument("--secret-file", default=None, help="Path to file containing HMAC secret.")
    p_vh.set_defaults(func=cmd_ota_verify_hmac)

    # --- ota-bundle ---
    p_b = sub.add_parser("ota-bundle", help="Build assignment OTA bundle folder/zip from SessionRecord.")
    p_b.add_argument("--session", required=True, help="Path to session.json (SessionRecord).")
    p_b.add_argument("--out", required=True, help="Output directory root.")
    p_b.add_argument("--name", default=None, help="Optional bundle folder name override.")
    p_b.add_argument("--product", default="smart-guitar", help="Product name (manifest routing).")
    p_b.add_argument("--device-model", default=None, help="Target device model.")
    p_b.add_argument("--min-firmware", default=None, help="Target minimum firmware.")
    p_b.add_argument("--zip", action="store_true", help="Also create bundle.zip.")
    p_b.add_argument("--secret", default=None, help="HMAC secret for signing.")
    p_b.add_argument("--secret-file", default=None, help="Path to file containing HMAC secret.")
    p_b.set_defaults(func=cmd_ota_bundle)

    # --- ota-verify-folder ---
    p_vf = sub.add_parser("ota-verify-folder", help="Verify bundle folder integrity against manifest.")
    p_vf.add_argument("bundle_dir", help="Path to bundle directory (folder).")
    p_vf.set_defaults(func=cmd_ota_verify_folder)

    # --- ota-verify-zip ---
    p_z = sub.add_parser("ota-verify-zip", help="Verify bundle.zip by extracting and verifying.")
    p_z.add_argument("zip_path", help="Path to bundle.zip")
    p_z.add_argument("--secret", default=None, help="HMAC secret for signature verification.")
    p_z.add_argument("--secret-file", default=None, help="Path to file containing HMAC secret.")
    p_z.set_defaults(func=cmd_ota_verify_zip)


    # --- dance-pack-list ---
    p_dpl = sub.add_parser("dance-pack-list", help="List all bundled dance packs.")
    p_dpl.add_argument("--json", action="store_true", help="Output as JSON.")
    p_dpl.set_defaults(func=cmd_dance_pack_list)

    # --- dance-pack-set-list ---
    p_dsl = sub.add_parser("dance-pack-set-list", help="List all bundled dance pack sets.")
    p_dsl.add_argument("--json", action="store_true", help="Output as JSON.")
    p_dsl.set_defaults(func=cmd_dance_pack_set_list)

    # --- dance-pack-set-validate ---
    p_dsv = sub.add_parser("dance-pack-set-validate", help="Validate pack set references.")
    p_dsv.add_argument("set_id", nargs="?", help="Pack set ID (bundled).")
    p_dsv.add_argument("--path", default=None, help="Path to pack set YAML file.")
    p_dsv.add_argument("--quiet", "-q", action="store_true", help="Suppress output on success.")
    p_dsv.set_defaults(func=cmd_dance_pack_set_validate)

    # --- dance-pack-set-show ---
    p_dss = sub.add_parser("dance-pack-set-show", help="Show pack set summary.")
    p_dss.add_argument("set_id", help="Pack set ID.")
    p_dss.add_argument("--json", action="store_true", help="Output as JSON.")
    p_dss.set_defaults(func=cmd_dance_pack_set_show)

    return p


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    if argv is None:
        argv = sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        return 130
    except FileNotFoundError as e:
        print(f"ERROR: file not found: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
