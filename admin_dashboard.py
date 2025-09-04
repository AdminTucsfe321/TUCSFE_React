import streamlit as st
import pandas as pd
import os
import logging

# Logger setup
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s [%(name)s]: %(message)s",
        level=logging.INFO
    )

def render_admin_dashboard():
    logger.info("Admin dashboard rendering started.")
    st.title("Admin Dashboard")

    feedback_path = "data/feedback.csv"
    session_path = "data/session_log.csv"

    # Session Logs
    if os.path.exists(session_path):
        try:
            df_sessions = pd.read_csv(session_path)
            total_sessions = df_sessions[df_sessions.event_type == 'login'].shape[0]
            total_queries = df_sessions[df_sessions.event_type == 'query'].shape[0]
            logger.info(f"Loaded session log with {len(df_sessions)} records.")
            logger.info(f"Total sessions: {total_sessions}, Total queries: {total_queries}")

            st.subheader("Session Usage Log")
            st.write(f"Total sessions: {total_sessions}")
            st.write(f"Total queries: {total_queries}")
            st.dataframe(df_sessions.tail(15))
        except Exception as e:
            logger.error(f"Failed to load or display session logs: {e}", exc_info=True)
            st.error("Failed to load session logs.")
    else:
        logger.warning(f"Session log file not found: {session_path}")
        st.info("No session logs yet.")

    # Feedback Logs
    if os.path.exists(feedback_path):
        try:
            df_feedback = pd.read_csv(feedback_path)
            logger.info(f"Loaded feedback log with {len(df_feedback)} records.")
            if 'rating' in df_feedback.columns:
                avg_rating = df_feedback['rating'].mean()
                logger.info(f"Average feedback rating: {avg_rating:.2f}")
                st.subheader("Feedback")
                st.write(f"Avg feedback rating: {avg_rating:.2f}")
            else:
                logger.warning("Feedback data has no 'rating' column.")
                st.subheader("Feedback")
                st.write("No feedback ratings available.")
            st.dataframe(df_feedback.tail(15))
        except Exception as e:
            logger.error(f"Failed to load or display feedback data: {e}", exc_info=True)
            st.error("Failed to load feedback data.")
    else:
        logger.warning(f"Feedback file not found: {feedback_path}")
        st.info("No feedback data found.")

    logger.info("Admin dashboard rendering completed.")
