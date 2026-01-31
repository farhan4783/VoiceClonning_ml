import { motion } from 'framer-motion';
import { FaMicrophone, FaRobot, FaMagic } from 'react-icons/fa';
import './Hero.css';

const Hero = () => {
    return (
        <section className="hero">
            <div className="container">
                <motion.div
                    className="hero-content"
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <motion.div
                        className="hero-badge"
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.2 }}
                    >
                        <FaRobot /> Powered by AI
                    </motion.div>

                    <h1 className="hero-title">
                        Clone Your Voice with
                        <span className="gradient-text"> AI Magic</span>
                    </h1>

                    <p className="hero-description">
                        Record just 30 seconds of your voice and watch as our advanced AI creates
                        a personalized voice model. Type any text and hear it spoken in your own voice.
                    </p>

                    <motion.div
                        className="hero-features"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 }}
                    >
                        <div className="feature-item">
                            <div className="feature-icon">
                                <FaMicrophone />
                            </div>
                            <div className="feature-text">
                                <h3>30-Second Recording</h3>
                                <p>Quick and easy voice capture</p>
                            </div>
                        </div>

                        <div className="feature-item">
                            <div className="feature-icon">
                                <FaRobot />
                            </div>
                            <div className="feature-text">
                                <h3>AI Voice Cloning</h3>
                                <p>Advanced neural synthesis</p>
                            </div>
                        </div>

                        <div className="feature-item">
                            <div className="feature-icon">
                                <FaMagic />
                            </div>
                            <div className="feature-text">
                                <h3>Instant Synthesis</h3>
                                <p>Generate speech in seconds</p>
                            </div>
                        </div>
                    </motion.div>

                    <motion.div
                        className="hero-cta"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                    >
                        <button
                            className="btn btn-primary btn-lg"
                            onClick={() => {
                                document.querySelector('.section')?.scrollIntoView({ behavior: 'smooth' });
                            }}
                        >
                            Get Started
                        </button>
                    </motion.div>
                </motion.div>
            </div>

            {/* Floating particles effect */}
            <div className="particles">
                {[...Array(20)].map((_, i) => (
                    <motion.div
                        key={i}
                        className="particle"
                        initial={{
                            x: Math.random() * window.innerWidth,
                            y: Math.random() * window.innerHeight,
                        }}
                        animate={{
                            y: [null, Math.random() * -100 - 50],
                            opacity: [0, 1, 0],
                        }}
                        transition={{
                            duration: Math.random() * 3 + 2,
                            repeat: Infinity,
                            delay: Math.random() * 2,
                        }}
                    />
                ))}
            </div>
        </section>
    );
};

export default Hero;
