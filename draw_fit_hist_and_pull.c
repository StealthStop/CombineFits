#include "draw_fit_hist_and_pull_plot.c"

void draw_fit_hist_and_pull( const char* path = "", const char* fitfile_name = "",
               const char* sig1_name = "RPV 450",
               const char* year_prefix = "",
               const char* outFileSuffix = "",
               bool sig_fit = false, bool draw_sig_norm_1 = true,
               bool draw_fit_components = false,
               const char* fitfile_second_signal_name    = "",
               const char* sig2_name = "RPV 650"
               ) {
    
      char fitfile[400];
      char fitfile_second_signal[400];
      sprintf( fitfile, "%s%s", path, fitfile_name ) ;      
      sprintf( fitfile_second_signal, "%s%s", path, fitfile_second_signal_name ) ;      

      gDirectory -> cd( "Rint:/" ) ;
      TCanvas* can = (TCanvas*) gDirectory -> FindObject( "can1" ) ;
      if ( can == 0x0 ) can = new TCanvas( "can1", "", 700, 900 ) ;
      can -> Draw() ;
      TPad* canpad =  (TPad*) can -> cd() ;
      can -> Clear() ;
      gStyle -> SetPadLeftMargin(0.15) ;
      gStyle -> SetPadTopMargin(0.20) ;

      double chi2_sum[10] ;
      int    chi2_npoints[10] ;
      TPad* tpc = new TPad( "canpad","canpad", 0., 0., 1., 1. ) ;
      tpc -> Draw() ;
      tpc -> cd() ;
      TText* tt = new TText() ;
      tt -> SetTextSize( 0.02 ) ;
      float can_ymax = 0.95 ;

      for ( int ci=1; ci<=4; ci++ ) {
         can -> cd() ;

         char pname[100] ;
         sprintf( pname, "cp%d", ci ) ;
         double pxl, pxh, pyl, pyh ;
         if ( ci == 1 ) {
            pxl = 0.000 ; pxh = 0.499 ;
            pyl = can_ymax/2+0.001; pyh = can_ymax ;
         }
         if ( ci == 2 ) {
            pxl = 0.501 ; pxh = 1.000 ;
            pyl = can_ymax/2+0.001; pyh = can_ymax ;
         }
         if ( ci == 3 ) {
            pxl = 0.000 ; pxh = 0.499 ;
            pyl = 0.000 ; pyh = can_ymax/2-0.001 ;
         }
         if ( ci == 4 ) {
            pxl = 0.501 ; pxh = 1.000 ;
            pyl = 0.000 ; pyh = can_ymax/2-0.001 ;
         }
         TPad* tp = new TPad( pname, pname, pxl, pyl, pxh, pyh ) ;
         tp -> Draw() ;
         tp -> cd() ;

         char bin_name[100] ;
         sprintf( bin_name, "%sD%d", year_prefix, ci ) ;

         draw_fit_hist_and_pull_plot( chi2_sum[ci], chi2_npoints[ci], outFileSuffix,  bin_name, sig_fit, draw_sig_norm_1, draw_fit_components, fitfile, sig1_name, fitfile_second_signal, sig2_name ) ;

         tp->cd();
         TLatex mark; mark.SetNDC(true);
         mark.SetTextAlign(11);
         mark.SetTextSize(0.055);
         mark.SetTextFont(61);
         mark.DrawLatex(0.515, 0.9315, "CMS");
         mark.SetTextFont(52);
         mark.DrawLatex(0.65, 0.93, "Simulation");
         mark.Draw("SAME");
      }

      double total_chi2_sum(0.) ;
      int    total_chi2_npoints(0) ;
      for ( int di=1; di<=4; di++ ) {
         total_chi2_sum += chi2_sum[di] ;
         total_chi2_npoints += chi2_npoints[di] ;
      }
      int ndof = total_chi2_npoints - 3 - 4 ;
      if ( sig_fit ) ndof -- ;
      can -> Update(); 
      can -> Draw(); 
      gSystem -> ProcessEvents() ;

      tpc -> cd() ;
      TText* tt2 = new TText() ;
      tt2 -> SetTextAlign(13) ;
      tt2 -> SetTextSize(0.025) ;
      tt2 -> SetTextColor(2) ;
      char chistr[100] ;
      if ( sig_fit ) {
         sprintf( chistr, "S+B fit total chi2 = %7.2f", total_chi2_sum ) ;
      } else {
         sprintf( chistr, "B-only fit total chi2 = %7.2f", total_chi2_sum ) ;
      }
      tt2 -> DrawTextNDC( 0.04, 0.97, chistr ) ;
      tpc -> Update() ; tpc -> Draw() ; gSystem -> ProcessEvents() ;

      gSystem -> Exec( "mkdir -p outputfiles" ) ;
      if ( sig_fit ) {
         can -> SaveAs( "outputfiles/fit-hist-and-pull-s.pdf" ) ;
      } else {
         can -> SaveAs( "outputfiles/fit-hist-and-pull-b.pdf" ) ;
      }
   }

