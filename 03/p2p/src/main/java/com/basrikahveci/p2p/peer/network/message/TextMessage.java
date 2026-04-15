package com.basrikahveci.p2p.peer.network.message;

import com.basrikahveci.p2p.peer.Peer;
import com.basrikahveci.p2p.peer.network.Connection;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TextMessage implements Message {

    private static final Logger LOGGER = LoggerFactory.getLogger(TextMessage.class);

    private static final long serialVersionUID = 1L;

    private final String sender;
    private final String content;

    public TextMessage(String sender, String content) {
        this.sender = sender;
        this.content = content;
    }

    public String getSender() {
        return sender;
    }

    public String getContent() {
        return content;
    }

    @Override
    public void handle(Peer peer, Connection connection) {
        // Here we just log the received message using system out to ensure the user can
        // see it in terminal
        System.out.println("\n>>> [TEXT MESSAGE] From " + sender + ": " + content + "\n");
        // Also log to the logger
        LOGGER.info("Received TextMessage from {}: {}", sender, content);
    }
}
