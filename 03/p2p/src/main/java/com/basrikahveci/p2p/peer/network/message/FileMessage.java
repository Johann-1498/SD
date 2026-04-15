package com.basrikahveci.p2p.peer.network.message;

import com.basrikahveci.p2p.peer.Peer;
import com.basrikahveci.p2p.peer.network.Connection;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileOutputStream;
import java.io.File;
import java.io.IOException;

public class FileMessage implements Message {

    private static final Logger LOGGER = LoggerFactory.getLogger(FileMessage.class);

    private static final long serialVersionUID = 1L;

    private final String sender;
    private final String fileName;
    private final byte[] fileData;

    public FileMessage(String sender, String fileName, byte[] fileData) {
        this.sender = sender;
        this.fileName = fileName;
        this.fileData = fileData;
    }

    public String getSender() {
        return sender;
    }

    public String getFileName() {
        return fileName;
    }

    public byte[] getFileData() {
        return fileData;
    }

    @Override
    public void handle(Peer peer, Connection connection) {
        System.out.println("\n>>> [FILE MESSAGE] Received file '" + fileName + "' (" + fileData.length + " bytes) from "
                + sender + "\n");

        try {
            // Save file in the current working directory, prefixing with my peer name or
            // receiver peer name to avoid conflicts if running in the same directory
            String saveAs = peer.getConfig().getPeerName() + "_received_" + fileName;
            File file = new File(saveAs);
            try (FileOutputStream fos = new FileOutputStream(file)) {
                fos.write(fileData);
            }
            System.out.println(">>> File saved to: " + file.getAbsolutePath() + "\n");
            LOGGER.info("Saved received file from '{}' to '{}'", sender, saveAs);
        } catch (IOException e) {
            System.err.println(">>> Failed to save the received file: " + e.getMessage());
            LOGGER.error("Error saving file received from " + sender, e);
        }
    }
}
