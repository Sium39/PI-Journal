// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/**
 * PureChain Smart Contracts for Military Logistics 
 * Registers PI-containers, validates PUF data, enforces RBAC
 * Deployed on Pure Chain PoA² network
 * Author: Sium Bin Noor <siumbinmoor@kumoh.ac.kr>
 */
contract PureChainLogistics is AccessControl, Pausable {
    using ECDSA for bytes32;
    
    bytes32 public constant MILITARY_ADMIN = keccak256("MILITARY_ADMIN");
    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR");
    bytes32 public constant CONTAINER_ROLE = keccak256("CONTAINER");
    
    struct ContainerRecord {
        string containerId;
        bytes32 pufHash;      // SHA256(PUF||skew)
        uint256 registeredAt;
        uint256 lastSync;
        bool active;
        mapping(bytes32 => bool) txHashes;  // Prevent replays
    }
    
    mapping(string => ContainerRecord) public containers;
    mapping(bytes32 => bool) public processedTxs;
    
    uint256 public totalRecords;
    uint256 public constant MAX_BUFFER_AGE = 1 hours;  // Resilience timeout
    
    event ContainerRegistered(string indexed containerId, bytes32 pufHash);
    event DataLogged(string indexed containerId, bytes32 txHash, uint256 timestamp);
    event SpoofDetected(string indexed containerId, bytes32 invalidHash);
    event BatchSynced(string indexed containerId, uint256 txCount);
    
    modifier onlyMilitary() {
        require(hasRole(MILITARY_ADMIN, msg.sender), "Only military admin");
        _;
    }
    
    modifier validContainer(string memory containerId) {
        require(containers[containerId].active, "Container not registered");
        _;
    }
    
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MILITARY_ADMIN, msg.sender);
    }
    
    /**
     * Line 2: Deploy registration module
     * Register PI-container with PUF hardware binding
     */
    function registerContainer(
        string memory containerId,
        bytes32 pufHash,
        bytes memory pubKey  // ECDSA public key
    ) external onlyRole(MILITARY_ADMIN) {
        require(bytes(containerId).length > 0, "Invalid ID");
        require(pufHash != bytes32(0), "Invalid PUF");
        
        containers[containerId] = ContainerRecord({
            containerId: containerId,
            pufHash: pufHash,
            registeredAt: block.timestamp,
            lastSync: block.timestamp,
            active: true
        });
        
        _grantRole(CONTAINER_ROLE, address(uint160(uint256(keccak256(abi.encodePacked(pubKey))))));
        
        emit ContainerRegistered(containerId, pufHash);
        totalRecords++;
    }
    
    /**
     * Edge device logs inspection data (YOLO+IoT)
     */
    function logInspectionData(
        string memory containerId,
        bytes32 dataHash,    // SHA256(sensor_data + yolo_output)
        bytes32 signature,   // ECDSA sig
        bytes32 txHash       // SHA256(tx_id + dataHash)
    ) external whenNotPaused validContainer(containerId) {
        ContainerRecord storage container = containers[containerId];
        
        // Liveness \& replay protection (line 7-8)
        require(!processedTxs[txHash], "Tx already processed");
        require(block.timestamp - container.lastSync < MAX_BUFFER_AGE, "Buffer expired");
        
        // PUF validation (line 7)
        require(dataHash == container.pufHash, "PUF mismatch - spoof detected");
        
        // RBAC: only registered container (line 10)
        bytes32 messageHash = keccak256(abi.encodePacked(containerId, dataHash));
        require(messageHash.recover(signature) == msg.sender, "Invalid signature");
        
        // Commit to ledger (line 13)
        processedTxs[txHash] = true;
        container.lastSync = block.timestamp;
        
        emit DataLogged(containerId, txHash, block.timestamp);
    }
    
    /**
     * Recover from intermittent connectivity
     */
    function batchSync(
        string memory containerId,
        bytes32[] memory txHashes,
        bytes32[] memory signatures
    ) external validContainer(containerId) {
        require(txHashes.length == signatures.length, "Mismatched arrays");
        require(txHashes.length <= 100, "Max 100 tx per batch");  // Gas optimization
        
        uint256 synced = 0;
        for (uint i = 0; i < txHashes.length; i++) {
            if (!processedTxs[txHashes[i]]) {
                processedTxs[txHashes[i]] = true;
                synced++;
            }
        }
        
        containers[containerId].lastSync = block.timestamp;
        emit BatchSync(containerId, synced);
    }
    
  
    function verifyDataIntegrity(
        string memory containerId,
        bytes32 dataHash,
        bytes32 txHash
    ) external view returns (bool) {
        return processedTxs[txHash] && dataHash == containers[containerId].pufHash;
    }
    
    /**
     * Emergency pause (military command)
     */
    function pause() external onlyRole(MILITARY_ADMIN) {
        _pause();
    }
    
    function unpause() external onlyRole(MILITARY_ADMIN) {
        _unpause();
    }
    
    function getContainerStatus(string memory containerId) external view returns (
        bool active,
        uint256 lastSync,
        uint256 age
    ) {
        ContainerRecord memory c = containers[containerId];
        return (c.active, c.lastSync, block.timestamp - c.lastSync);
    }
}
