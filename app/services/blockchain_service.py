"""Servicio de blockchain: hash de la receta, anclaje en el contrato y QR (spec §8.4).

Tolerante a fallos de conexión: el llamador decide qué hacer si la cadena no responde.
"""
import hashlib
import logging
from io import BytesIO

import qrcode
from web3 import Web3

from app.core.config import settings

logger = logging.getLogger(__name__)

# ABI mínima del contrato RegistroRecetas (solo lo que usamos)
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "idReceta", "type": "uint256"},
            {"internalType": "bytes32", "name": "hashReceta", "type": "bytes32"},
        ],
        "name": "registrarReceta",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "idReceta", "type": "uint256"}],
        "name": "obtenerHash",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
]

_w3 = None
_contract = None
_account = None


def _setup():
    global _w3, _contract, _account
    if _w3 is None:
        _w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_URL))
        _account = _w3.eth.account.from_key(settings.BLOCKCHAIN_PRIVATE_KEY)
        _contract = _w3.eth.contract(
            address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS), abi=CONTRACT_ABI
        )
    return _w3, _contract, _account


def blockchain_disponible() -> bool:
    try:
        w3, _, _ = _setup()
        return w3.is_connected()
    except Exception:  # noqa: BLE001
        return False


def generar_hash_receta(receta) -> str:
    """Hash SHA-256 determinista del contenido de la receta (devuelve '0x' + 64 hex)."""
    medico = receta.usuario
    partes = [
        f"receta:{receta.id_receta}",
        f"paciente:{receta.paciente.ci}",
        f"medico:{medico.numero_licencia or medico.id_usuario}",
        f"diagnostico:{receta.id_diagnostico}",
    ]
    for rm in sorted(receta.medicamentos, key=lambda m: m.id_receta_med):
        partes.append(f"med:{rm.id_medicamento}|{rm.dosis}|{rm.frecuencia}|{rm.duracion}")
    canonical = "||".join(partes)
    return "0x" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def registrar_en_blockchain(id_receta: int, hash_hex: str) -> dict:
    """Ancla el hash en el contrato. Devuelve metadatos del bloque/tx."""
    w3, contract, account = _setup()
    hash_bytes = bytes.fromhex(hash_hex[2:] if hash_hex.startswith("0x") else hash_hex)

    tx = contract.functions.registrarReceta(id_receta, hash_bytes).build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
        }
    )
    signed = account.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or getattr(signed, "rawTransaction")
    tx_hash = w3.eth.send_raw_transaction(raw)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    return {
        "bloque_id": str(receipt.blockNumber),
        "tx_hash": tx_hash.hex(),
        "direccion_contrato": settings.CONTRACT_ADDRESS,
    }


def obtener_hash_blockchain(id_receta: int) -> str:
    """Lee el hash anclado para una receta ('0x000…0' si no existe)."""
    _, contract, _ = _setup()
    valor = contract.functions.obtenerHash(id_receta).call()
    return "0x" + (valor.hex() if isinstance(valor, (bytes, bytearray)) else str(valor))


def generar_qr_png(payload: str) -> bytes:
    """Genera un PNG con el QR del payload (id + hash)."""
    img = qrcode.make(payload)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()
