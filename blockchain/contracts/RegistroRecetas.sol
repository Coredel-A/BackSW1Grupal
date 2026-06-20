// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title RegistroRecetas
/// @notice Almacena de forma inalterable el hash de cada receta emitida.
///         Solo guarda la huella (hash), nunca datos clínicos del paciente.
contract RegistroRecetas {
    // id_receta => hash de la receta
    mapping(uint256 => bytes32) private hashes;

    event RecetaRegistrada(uint256 indexed idReceta, bytes32 hashReceta);

    /// @notice Registra (ancla) el hash de una receta. Si ya existía, se respeta el original.
    function registrarReceta(uint256 idReceta, bytes32 hashReceta) external {
        require(hashes[idReceta] == bytes32(0), "La receta ya fue registrada");
        hashes[idReceta] = hashReceta;
        emit RecetaRegistrada(idReceta, hashReceta);
    }

    /// @notice Devuelve el hash anclado de una receta (bytes32(0) si no existe).
    function obtenerHash(uint256 idReceta) external view returns (bytes32) {
        return hashes[idReceta];
    }
}
