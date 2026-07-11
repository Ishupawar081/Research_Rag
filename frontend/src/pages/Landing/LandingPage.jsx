import { Box, Typography, Button, Container, Grid, Card, CardContent, useTheme } from "@mui/material";
import { motion } from "framer-motion";
import SpaceBackground from "./SpaceBackground";
import { useNavigate } from "react-router-dom";
import { 
  FileText, Library, GitCompare, Search, Zap, Layers, 
  Network, BookOpen, UserPlus, FileUp, Sparkles, MessageSquare, Shield,
  ArrowRight, FileSearch
} from "lucide-react";

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.2 }
  }
};

export default function LandingPage() {
    const navigate = useNavigate();
    const theme = useTheme();

    return (
        <Box sx={{
            width: "100%",
            bgcolor: "#0B1120",
            color: "#F8FAFC",
            minHeight: "100vh",
            overflowX: "hidden"
        }}>
            
            {/* HERO SECTION */}
            <Box sx={{
                position: "relative",
                width: "100%",
                minHeight: "100vh",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                textAlign: "center",
                px: 2
            }}>
                <Box sx={{ position: "absolute", width: "100%", height: "100%", zIndex: 0 }}>
                    <SpaceBackground />
                </Box>
                
                <Box sx={{ position: "relative", zIndex: 10, maxWidth: "800px" }}>
                    <motion.div initial="hidden" animate="visible" variants={fadeIn}>
                        <Typography variant="h1" sx={{
                            fontSize: { xs: "3rem", md: "5rem" },
                            fontWeight: 800,
                            letterSpacing: "-0.04em",
                            lineHeight: 1.1,
                            mb: 3,
                            background: "linear-gradient(to right, #ffffff, #A78BFA)",
                            WebkitBackgroundClip: "text",
                            WebkitTextFillColor: "transparent",
                            textShadow: "0 0 40px rgba(139,92,246,0.3)"
                        }}>
                            AI Research Assistant
                        </Typography>
                    </motion.div>

                    <motion.div initial="hidden" animate="visible" variants={fadeIn} transition={{ delay: 0.2 }}>
                        <Typography variant="h5" sx={{
                            color: "#94A3B8",
                            fontWeight: 400,
                            mb: 4,
                            lineHeight: 1.6
                        }}>
                            Your intelligent workspace for understanding scientific literature.
                        </Typography>
                        
                        <Typography variant="body1" sx={{ color: "#64748B", mb: 6, fontSize: "1.1rem" }}>
                            Upload research papers, ask questions, compare publications, search your personal library and discover insights using AI-powered semantic retrieval.
                        </Typography>
                    </motion.div>

                    <motion.div initial="hidden" animate="visible" variants={fadeIn} transition={{ delay: 0.4 }}>
                        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                            <Button 
                                onClick={() => navigate("/auth")}
                                sx={{
                                    px: 5, py: 2,
                                    borderRadius: "30px",
                                    background: "linear-gradient(135deg, rgba(139,92,246,0.9) 0%, rgba(59,130,246,0.9) 100%)",
                                    color: "white",
                                    fontSize: "1.1rem",
                                    fontWeight: 600,
                                    textTransform: "none",
                                    boxShadow: "0 0 20px rgba(139,92,246,0.3)",
                                    "&:hover": { background: "linear-gradient(135deg, rgba(139,92,246,1) 0%, rgba(59,130,246,1) 100%)" }
                                }}
                            >
                                Get Started
                            </Button>
                            <Button 
                                onClick={() => document.getElementById("features").scrollIntoView({ behavior: 'smooth' })}
                                sx={{
                                    px: 5, py: 2,
                                    borderRadius: "30px",
                                    border: "1px solid rgba(255,255,255,0.2)",
                                    color: "white",
                                    fontSize: "1.1rem",
                                    fontWeight: 600,
                                    textTransform: "none",
                                    "&:hover": { bgcolor: "rgba(255,255,255,0.05)" }
                                }}
                            >
                                Learn More
                            </Button>
                        </Box>
                    </motion.div>
                </Box>
            </Box>

            {/* WHAT CAN YOU DO? (FEATURES) */}
            <Box id="features" sx={{ py: 15, bgcolor: "rgba(11,17,32,0.95)", position: "relative", zIndex: 1 }}>
                <Container maxWidth="lg">
                    <Typography variant="h3" sx={{ textAlign: "center", fontWeight: 700, mb: 8, color: "white" }}>
                        What Can You Do?
                    </Typography>
                    
                    <Grid container spacing={4}>
                        {[
                            {
                                icon: <FileText size={40} color="#8B5CF6" />,
                                title: "Single Paper Chat",
                                desc: "Chat with one research paper. Ask about methodology, datasets, results, limitations, or future work.",
                            },
                            {
                                icon: <Library size={40} color="#3B82F6" />,
                                title: "Collection Chat",
                                desc: "Search across all uploaded papers. E.g., 'What papers use ImageNet?' or 'Which use reinforcement learning?'",
                            },
                            {
                                icon: <GitCompare size={40} color="#EC4899" />,
                                title: "Compare Papers",
                                desc: "Generate structured comparisons. Compare methodology, datasets, experiments, results, and advantages.",
                            }
                        ].map((feat, idx) => (
                            <Grid item xs={12} md={4} key={idx}>
                                <motion.div whileHover={{ y: -10 }} transition={{ duration: 0.3 }}>
                                    <Card sx={{ 
                                        bgcolor: "rgba(30,41,59,0.5)", 
                                        backdropFilter: "blur(10px)",
                                        border: "1px solid rgba(255,255,255,0.05)",
                                        borderRadius: 4,
                                        height: "100%",
                                        color: "white"
                                    }}>
                                        <CardContent sx={{ p: 4, textAlign: "center" }}>
                                            <Box sx={{ mb: 3 }}>{feat.icon}</Box>
                                            <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>{feat.title}</Typography>
                                            <Typography variant="body1" sx={{ color: "#94A3B8", lineHeight: 1.7 }}>
                                                {feat.desc}
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            </Grid>
                        ))}
                    </Grid>
                </Container>
            </Box>

            {/* HOW IT WORKS (PIPELINE) */}
            <Box sx={{ py: 15, bgcolor: "#0f172a" }}>
                <Container maxWidth="lg">
                    <Typography variant="h3" sx={{ textAlign: "center", fontWeight: 700, mb: 10, color: "white" }}>
                        How It Works
                    </Typography>
                    
                    <Box sx={{ 
                        display: 'flex', 
                        flexWrap: 'wrap',
                        justifyContent: 'center', 
                        alignItems: 'center',
                        gap: 2
                    }}>
                        {[
                            { name: "Upload PDF", icon: <FileUp size={30} /> },
                            { name: "Parse", icon: <Layers size={30} /> },
                            { name: "Graph", icon: <Network size={30} /> },
                            { name: "Embed", icon: <Sparkles size={30} /> },
                            { name: "Retrieve", icon: <FileSearch size={30} /> },
                            { name: "Answer", icon: <MessageSquare size={30} /> },
                        ].map((step, idx, arr) => (
                            <Box key={idx} sx={{ display: 'flex', alignItems: 'center' }}>
                                <Box sx={{ 
                                    textAlign: 'center', 
                                    p: 3, 
                                    bgcolor: "rgba(139,92,246,0.1)", 
                                    borderRadius: 3,
                                    border: "1px solid rgba(139,92,246,0.2)",
                                    color: "#A78BFA",
                                    minWidth: 120
                                }}>
                                    {step.icon}
                                    <Typography sx={{ mt: 1, fontWeight: 600, fontSize: "0.9rem" }}>{step.name}</Typography>
                                </Box>
                                {idx < arr.length - 1 && (
                                    <ArrowRight size={24} color="#475569" style={{ margin: "0 10px" }} />
                                )}
                            </Box>
                        ))}
                    </Box>
                </Container>
            </Box>

            {/* WHY THIS IS DIFFERENT */}
            <Box sx={{ py: 15, bgcolor: "rgba(11,17,32,0.95)" }}>
                <Container maxWidth="lg">
                    <Typography variant="h3" sx={{ textAlign: "center", fontWeight: 700, mb: 8, color: "white" }}>
                        Why This Is Different
                    </Typography>
                    
                    <Grid container spacing={3}>
                        {[
                            "Semantic Retrieval", "Knowledge Graph", "Source Citations", 
                            "Multi-Paper Search", "Paper Comparison", "Fast Local LLM", 
                            "Modern UI", "Grounded Responses"
                        ].map((feature, i) => (
                            <Grid item xs={12} sm={6} md={3} key={i}>
                                <Box sx={{
                                    p: 3, 
                                    bgcolor: "rgba(255,255,255,0.03)",
                                    border: "1px solid rgba(255,255,255,0.05)",
                                    borderRadius: 2,
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 2
                                }}>
                                    <Shield size={20} color="#3B82F6" />
                                    <Typography sx={{ fontWeight: 500 }}>{feature}</Typography>
                                </Box>
                            </Grid>
                        ))}
                    </Grid>
                </Container>
            </Box>

            {/* HOW TO USE */}
            <Box sx={{ py: 15, bgcolor: "#0f172a" }}>
                <Container maxWidth="md">
                    <Typography variant="h3" sx={{ textAlign: "center", fontWeight: 700, mb: 8, color: "white" }}>
                        How To Use
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        {[
                            { num: "1", title: "Create an account", icon: <UserPlus size={24}/> },
                            { num: "2", title: "Upload research papers", icon: <FileUp size={24}/> },
                            { num: "3", title: "Choose chat mode (Single, Collection, Compare)", icon: <Layers size={24}/> },
                            { num: "4", title: "Ask questions and explore", icon: <MessageSquare size={24}/> }
                        ].map((step, i) => (
                            <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 3, p: 3, bgcolor: "rgba(0,0,0,0.2)", borderRadius: 3 }}>
                                <Box sx={{ 
                                    width: 50, height: 50, borderRadius: '50%', 
                                    bgcolor: "#8B5CF6", color: "white", 
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    fontWeight: 'bold', fontSize: '1.2rem'
                                }}>
                                    {step.num}
                                </Box>
                                <Typography variant="h6">{step.title}</Typography>
                                <Box sx={{ ml: 'auto', color: "#64748B" }}>{step.icon}</Box>
                            </Box>
                        ))}
                    </Box>
                </Container>
            </Box>

            {/* EXAMPLE QUESTIONS */}
            <Box sx={{ py: 15, bgcolor: "rgba(11,17,32,0.95)" }}>
                <Container maxWidth="lg">
                    <Typography variant="h3" sx={{ textAlign: "center", fontWeight: 700, mb: 8, color: "white" }}>
                        Example Questions
                    </Typography>
                    <Grid container spacing={4}>
                        {[
                            {
                                mode: "Single Paper",
                                queries: ["Summarize this paper.", "Explain the methodology.", "What datasets were used?", "What are the limitations?"]
                            },
                            {
                                mode: "Collection",
                                queries: ["Which papers use ImageNet?", "Summarize my collection.", "Compare trends across papers."]
                            },
                            {
                                mode: "Comparison",
                                queries: ["Compare these papers.", "Compare methodologies.", "Compare results."]
                            }
                        ].map((group, i) => (
                            <Grid item xs={12} md={4} key={i}>
                                <Typography variant="h6" sx={{ mb: 3, color: "#A78BFA", fontWeight: 600 }}>{group.mode}</Typography>
                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                    {group.queries.map((q, j) => (
                                        <Box key={j} sx={{ p: 2, bgcolor: "rgba(255,255,255,0.05)", borderRadius: 2, borderLeft: "3px solid #3B82F6" }}>
                                            "{q}"
                                        </Box>
                                    ))}
                                </Box>
                            </Grid>
                        ))}
                    </Grid>
                </Container>
            </Box>

            {/* TECHNOLOGY STACK */}
            <Box sx={{ py: 15, bgcolor: "#0f172a" }}>
                <Container maxWidth="lg" sx={{ textAlign: 'center' }}>
                    <Typography variant="h3" sx={{ fontWeight: 700, mb: 6, color: "white" }}>
                        Technology Stack
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 2 }}>
                        {["React", "FastAPI", "FAISS", "Sentence Transformers", "Docling", "Knowledge Graph", "Ollama", "Qwen"].map((tech, i) => (
                            <Box key={i} sx={{ 
                                px: 3, py: 1.5, 
                                bgcolor: "rgba(59,130,246,0.1)", 
                                border: "1px solid rgba(59,130,246,0.3)",
                                borderRadius: "20px",
                                color: "#93C5FD",
                                fontWeight: 500
                            }}>
                                {tech}
                            </Box>
                        ))}
                    </Box>
                </Container>
            </Box>

            {/* FOOTER */}
            <Box sx={{ py: 6, borderTop: "1px solid rgba(255,255,255,0.1)", bgcolor: "rgba(11,17,32,1)", textAlign: 'center' }}>
                <Typography sx={{ color: "#64748B", mb: 2 }}>
                    AI Research Assistant Platform &copy; 2026
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, color: "#94A3B8", fontSize: "0.9rem" }}>
                    <span style={{ cursor: 'pointer' }}>About</span>
                    <span style={{ cursor: 'pointer' }}>GitHub</span>
                    <span style={{ cursor: 'pointer' }}>Documentation</span>
                    <span style={{ cursor: 'pointer' }}>License</span>
                </Box>
            </Box>

        </Box>
    );
}
