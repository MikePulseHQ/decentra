// Voice chat functionality with WebRTC
class VoiceChat {
    constructor(ws, username) {
        this.ws = ws;
        this.username = username;
        this.peerConnections = new Map(); // Map of username -> RTCPeerConnection
        this.localStream = null;
        this.currentVoiceChannel = null;
        this.currentVoiceServer = null;
        this.inDirectCall = false;
        this.directCallPeer = null;
        this.isMuted = false;
        
        // ICE servers configuration (using public STUN servers)
        this.iceServers = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        };
    }
    
    async initLocalStream() {
        try {
            this.localStream = await navigator.mediaDevices.getUserMedia({ 
                audio: true, 
                video: false 
            });
            return true;
        } catch (error) {
            console.error('Error accessing microphone:', error);
            if (error.name === 'NotAllowedError') {
                alert('Microphone access denied. Please grant permission in your browser settings.');
            } else if (error.name === 'NotFoundError') {
                alert('No microphone found. Please connect a microphone and try again.');
            } else {
                alert('Cannot access microphone. Please check your permissions and device.');
            }
            return false;
        }
    }
    
    async joinVoiceChannel(serverId, channelId) {
        // Initialize local stream if not already done
        if (!this.localStream) {
            const success = await this.initLocalStream();
            if (!success) return;
        }
        
        this.currentVoiceServer = serverId;
        this.currentVoiceChannel = channelId;
        
        // Notify server
        this.ws.send(JSON.stringify({
            type: 'join_voice_channel',
            server_id: serverId,
            channel_id: channelId
        }));
    }
    
    leaveVoiceChannel() {
        // Close all peer connections
        this.peerConnections.forEach((pc, username) => {
            pc.close();
        });
        this.peerConnections.clear();
        
        // Notify server
        if (this.currentVoiceServer && this.currentVoiceChannel) {
            this.ws.send(JSON.stringify({
                type: 'leave_voice_channel'
            }));
        }
        
        this.currentVoiceServer = null;
        this.currentVoiceChannel = null;
        
        // Stop local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }
        
        this.isMuted = false;
    }
    
    async startDirectCall(friendUsername) {
        // Initialize local stream if not already done
        if (!this.localStream) {
            const success = await this.initLocalStream();
            if (!success) return;
        }
        
        this.inDirectCall = true;
        this.directCallPeer = friendUsername;
        
        // Notify server to signal the friend
        this.ws.send(JSON.stringify({
            type: 'start_voice_call',
            username: friendUsername
        }));
    }
    
    async acceptDirectCall(callerUsername) {
        // Initialize local stream
        if (!this.localStream) {
            const success = await this.initLocalStream();
            if (!success) return;
        }
        
        this.inDirectCall = true;
        this.directCallPeer = callerUsername;
        
        // Notify server that call is accepted
        this.ws.send(JSON.stringify({
            type: 'accept_voice_call',
            from: callerUsername
        }));
        
        // The caller will initiate the WebRTC connection
    }
    
    rejectDirectCall(callerUsername) {
        this.ws.send(JSON.stringify({
            type: 'reject_voice_call',
            from: callerUsername
        }));
    }
    
    endDirectCall() {
        if (this.directCallPeer && this.peerConnections.has(this.directCallPeer)) {
            this.peerConnections.get(this.directCallPeer).close();
            this.peerConnections.delete(this.directCallPeer);
        }
        
        this.inDirectCall = false;
        this.directCallPeer = null;
        
        // Stop local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }
        
        this.isMuted = false;
    }
    
    async createPeerConnection(targetUsername, isInitiator = true) {
        const pc = new RTCPeerConnection(this.iceServers);
        this.peerConnections.set(targetUsername, pc);
        
        // Add local stream tracks
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => {
                pc.addTrack(track, this.localStream);
            });
        }
        
        // Handle incoming tracks
        pc.ontrack = (event) => {
            console.log('Received remote track from', targetUsername);
            const remoteAudio = new Audio();
            remoteAudio.srcObject = event.streams[0];
            
            // Handle play promise to avoid unhandled rejection
            remoteAudio.play().catch(error => {
                console.warn('Audio autoplay failed:', error);
                // Audio will play when user interacts with the page
            });
            
            // Store audio element for later control
            pc.remoteAudio = remoteAudio;
        };
        
        // Handle ICE candidates
        pc.onicecandidate = (event) => {
            if (event.candidate) {
                this.ws.send(JSON.stringify({
                    type: 'webrtc_ice_candidate',
                    target: targetUsername,
                    candidate: event.candidate
                }));
            }
        };
        
        // Handle connection state changes
        pc.onconnectionstatechange = () => {
            console.log('Connection state with', targetUsername, ':', pc.connectionState);
            if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
                this.handlePeerDisconnected(targetUsername);
            }
        };
        
        // If initiator, create and send offer
        if (isInitiator) {
            try {
                const offer = await pc.createOffer();
                await pc.setLocalDescription(offer);
                
                this.ws.send(JSON.stringify({
                    type: 'webrtc_offer',
                    target: targetUsername,
                    offer: pc.localDescription,
                    context: {
                        server_id: this.currentVoiceServer,
                        channel_id: this.currentVoiceChannel
                    }
                }));
            } catch (error) {
                console.error('Error creating offer:', error);
            }
        }
        
        return pc;
    }
    
    async handleOffer(fromUsername, offer, context) {
        console.log('Received offer from', fromUsername);
        
        // Create peer connection if it doesn't exist
        let pc = this.peerConnections.get(fromUsername);
        if (!pc) {
            pc = await this.createPeerConnection(fromUsername, false);
        } else if (pc.signalingState === 'have-local-offer') {
            // Handle glare condition: both peers sent offers simultaneously
            console.log('Glare detected with', fromUsername, '- ignoring offer');
            return;
        }
        
        try {
            await pc.setRemoteDescription(new RTCSessionDescription(offer));
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            
            this.ws.send(JSON.stringify({
                type: 'webrtc_answer',
                target: fromUsername,
                answer: pc.localDescription
            }));
        } catch (error) {
            console.error('Error handling offer:', error);
        }
    }
    
    async handleAnswer(fromUsername, answer) {
        console.log('Received answer from', fromUsername);
        
        const pc = this.peerConnections.get(fromUsername);
        if (pc) {
            try {
                await pc.setRemoteDescription(new RTCSessionDescription(answer));
            } catch (error) {
                console.error('Error handling answer:', error);
            }
        }
    }
    
    async handleIceCandidate(fromUsername, candidate) {
        const pc = this.peerConnections.get(fromUsername);
        if (pc) {
            try {
                await pc.addIceCandidate(new RTCIceCandidate(candidate));
            } catch (error) {
                console.error('Error adding ICE candidate:', error);
            }
        }
    }
    
    handlePeerDisconnected(username) {
        console.log('Peer disconnected:', username);
        const pc = this.peerConnections.get(username);
        if (pc) {
            if (pc.remoteAudio) {
                pc.remoteAudio.pause();
                pc.remoteAudio.srcObject = null;
            }
            pc.close();
            this.peerConnections.delete(username);
        }
    }
    
    toggleMute() {
        if (this.localStream) {
            this.isMuted = !this.isMuted;
            this.localStream.getAudioTracks().forEach(track => {
                track.enabled = !this.isMuted;
            });
            
            // Notify server about mute state
            this.ws.send(JSON.stringify({
                type: 'voice_mute',
                muted: this.isMuted
            }));
            
            return this.isMuted;
        }
        return false;
    }
    
    // Handle voice state updates from server
    async handleVoiceStateUpdate(data) {
        const { username, state, voice_members, server_id, channel_id } = data;
        
        // Only handle if we're in the same voice channel
        if (this.currentVoiceServer !== server_id || this.currentVoiceChannel !== channel_id) {
            return;
        }
        
        if (state === 'joined' && username !== this.username) {
            // New user joined, create peer connection
            await this.createPeerConnection(username, true);
        } else if (state === 'left' && username !== this.username) {
            // User left, close connection
            this.handlePeerDisconnected(username);
        }
    }
}
