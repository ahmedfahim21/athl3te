// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IAthl3teStructs.sol";
import "./interfaces/IAthl3teEvents.sol";

// Interface to interact with core contract
interface IAthl3teCore {
    function isUserRegistered(address user) external view returns (bool);
}

contract Athl3teNFT is ERC721, Ownable, IAthl3teEvents {
    uint256 private _tokenIdCounter;
    mapping(uint256 => string) private _tokenURIs;

    address public coreContract;

    modifier onlyRegistered() {
        require(IAthl3teCore(coreContract).isUserRegistered(msg.sender), "Not registered");
        _;
    }

    constructor(string memory name, string memory symbol, address _coreContract) ERC721(name, symbol) Ownable() {
        _tokenIdCounter = 1; // Start token IDs from 1
        coreContract = _coreContract;
    }

    function mintNftWithUri(string memory uri) external onlyRegistered returns (uint256) {
        require(bytes(uri).length > 0, "URI cannot be empty");
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        _mint(msg.sender, tokenId);
        _tokenURIs[tokenId] = uri;
        emit Minted(msg.sender, tokenId, uri);
        return tokenId;
    }

    function getNftUri(uint256 tokenId) external view returns (string memory) {
        return _tokenURIs[tokenId];
    }

    // Override tokenURI to use our custom URI storage
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(ownerOf(tokenId) != address(0), "Token does not exist");
        return _tokenURIs[tokenId];
    }

    function getUserNftCount(address _user) external view returns (uint256) {
        return balanceOf(_user);
    }

    function getTotalNfts() external view returns (uint256) {
        return _tokenIdCounter - 1;
    }
}
